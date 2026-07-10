from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.ai_agent.parser import UserMessageParser
from src.ai_agent.schemas import AgentChatResponse, ExtractedUserData, UserIntent
from src.ai_agent.state import BOOKING_SESSIONS, BookingState, BookingStep
from src.ai_agent.trace import AgentTrace
from src.appointment.schemas import AppointmentCreate
from src.appointment.service import AppointmentService
from src.dental_service.service import DentalServiceService
from src.patient.schemas import PatientCreate
from src.patient.service import PatientService

MAX_MESSAGES_PER_SESSION = 20


class BookingAgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.patient_service = PatientService(db)
        self.dental_service_service = DentalServiceService(db)
        self.appointment_service = AppointmentService(db)
        self.parser = UserMessageParser()

    async def chat(
        self,
        session_id: str,
        message: str,
        phone: str | None = None,
    ) -> AgentChatResponse:
        trace = AgentTrace(session_id)

        state = self._get_or_create_state(session_id, phone)
        state.messages_count += 1

        if state.messages_count > MAX_MESSAGES_PER_SESSION:
            state.step = BookingStep.TRANSFERRED_TO_OPERATOR
            return self._response(
                state, "Я передам вас оператору, чтобы быстрее помочь с записью."
            )

        extracted = await self.parser.parse(message, state)

        trace.log(
            "user_message_parsed",
            {
                "message": message,
                "extracted": extracted.model_dump(),
                "state": state.model_dump(),
            },
        )

        self._merge_extracted_data(state, extracted)

        answer = await self._run_booking_flow(state, extracted, trace)

        BOOKING_SESSIONS[session_id] = state

        return self._response(state, answer)

    def _merge_extracted_data(
        self, state: BookingState, extracted: ExtractedUserData
    ) -> None:
        if extracted.patient_name:
            state.patient_name = extracted.patient_name

        if extracted.phone:
            state.phone = extracted.phone

        if extracted.service_query:
            state.service_query = extracted.service_query

        if extracted.target_date:
            state.target_date = extracted.target_date

        if extracted.selected_slot_index is not None:
            index = extracted.selected_slot_index - 1

            if 0 <= index < len(state.offered_slots):
                state.selected_slot = state.offered_slots[index]

    async def _run_booking_flow(
        self,
        state: BookingState,
        extracted: ExtractedUserData,
        trace: AgentTrace,
    ) -> str:
        if (
            extracted.wants_operator
            or extracted.intent == UserIntent.TRANSFER_TO_OPERATOR
        ):
            state.step = BookingStep.TRANSFERRED_TO_OPERATOR
            trace.log("transfer_to_operator")
            return "Сейчас передам вас оператору"

        if extracted.intent not in {
            UserIntent.BOOK_APPOINTMENT,
            UserIntent.UNKNOWN,
        }:
            return (
                "Я могу помочь с записью на прием"
                "Подскажите, пожалуйста, какая услуга вас интересует?"
            )

        if state.dental_service_id is None:
            if not state.service_query:
                state.step = BookingStep.COLLECTING_SERVICE
                return (
                    "Подскажите, пожалуйста, какая услуга вам нужна: "
                    "консультация, чистка, лечение кариеса или другая?"
                )

            await self._resolve_service(state, trace)

        if not state.patient_name:
            state.step = BookingStep.COLLECTING_PATIENT_NAME
            return "Подскажите, пожалуйста, как я могу к вам обращаться?"

        if not state.phone:
            state.step = BookingStep.COLLECTING_PHONE
            return "Подскажите, пожалуйста, ваш номер телефона для записи."

        if not state.target_date:
            state.step = BookingStep.COLLECTING_DATE
            return "На какой день вам удобно записаться?"

        if not state.offered_slots:
            return await self._search_and_offer_slots(state, trace)
        
        if not state.selected_slot:
            state.step = BookingStep.OFFERING_SLOTS
            return "Какой из предложенных вариантов вам подходит? Напишите номер: 1, 2 или 3."  # noqa: E501
        
        if extracted.confirmation is not True:
            state.step = BookingStep.WAITING_CONFIRMATION
            return self._build_confirmation_question(state)
        
        return await self._book_appointment(state, trace)
        

    async def _resolve_service(
        self,
        state: BookingState,
        trace: AgentTrace,
    ) -> None:
        service = (
            await self.dental_service_service.get_dental_service_by_name(
                state.service_query or ""
            )
        )

        state.dental_service_id = service.id
        state.dental_service_name = service.name

        trace.log(
            "service_resolved",
            {"service_id": service.id, "service_name": service.name},
        )

    async def _search_and_offer_slots(
        self,
        state: BookingState,
        trace: AgentTrace,
    ) -> str:
        if state.dental_service_id is None or state.target_date is None:
            return "Уточните, пожалуйста, услугу и дату для записи"

        slots = await self.appointment_service.get_free_slots(
            dental_service_id=state.dental_service_id,
            target_date=date.fromisoformat(state.target_date),
        )

        state.offered_slots = [
            {
                "doctor_id": slot.doctor_id,
                "doctor_name": slot.doctor_name,
                "dental_service_id": slot.dental_service_id,
                "start_time": slot.start_time.isoformat(),
                "end_time": slot.end_time.isoformat(),
            }
            for slot in slots[:3]
        ]

        trace.log(
            "slots_searched",
            {
                "dental_service_id": state.dental_service_id,
                "target_date": state.target_date,
                "slots_count": len(state.offered_slots),
            },
        )

        if not state.offered_slots:
            state.step = BookingStep.COLLECTING_DATE
            return (
                "На эту дату свободного времени нет. Хотите выбрать другой день?"
            )
            
        state.step = BookingStep.OFFERING_SLOTS
        
        return self._build_slots_answer(state)
    
    
    def _build_slots_answer(self, state: BookingState) -> str:
        rows = []

        for index, slot in enumerate(state.offered_slots, start=1):
            start_time = datetime.fromisoformat(slot["start_time"])
            rows.append(
                f"{index}. {start_time.strftime('%d.%m в %H:%M')} - "
                f"доктор {slot['doctor_name']}"
            )
            
        service_name = state.dental_service_name or "выбранную услугу"

        return (
            f"Нашел свободное время на {service_name}:\n"
            + "\n".join(rows)
            + "\nКакой вариант вам подходит?"
        )
        
    def _build_confirmation_question(self, state: BookingState) -> str:
        if not state.selected_slot:
            return "Уточните, пожалуйста, какой вариант вам подходит?"
        
        start_time = datetime.fromisoformat(state.selected_slot["start_time"])

        return (
            f"Подтвердите, пожалуйста: записать вас на "
            f"{start_time.strftime('%d.%m.%Y в %H:%M')} "
            f"к доктору {state.selected_slot['doctor_name']}"
        )

    async def _book_appointment(
        self,
        state: BookingState,
        trace: AgentTrace,
    ) -> str:
        if (
            not state.patient_name
            or not state.phone
            or not state.selected_slot
            or not state.dental_service_id
        ):
            return "Не хватает данных для записи. Давайте уточним детали."
        
        patient = await self.patient_service.get_or_create_by_phone(
            PatientCreate(
                name=state.patient_name,
                phone=state.phone
            )
        )
        
        appointment = await self.appointment_service.book_appointment(
            AppointmentCreate(
                patient_id=patient.id,
                doctor_id=state.selected_slot["doctor_id"],
                dental_service_id=state.dental_service_id,
                start_time=datetime.fromisoformat(state.selected_slot["start_time"])
            )
        )
        
        state.step = BookingStep.COMPLETED
        
        trace.log(
            "appointment_booked",
            {
                "appointment_id": appointment.id,
                "patient_id": patient.id,
                "start_time": appointment.start_time.isoformat()
            }
        )
        
        start_time = appointment.start_time.strftime("%d.%m.%Y в %H:%M")        

        return (
            f"Готово, {patient.name}. Записал вас на "
            f"{start_time} к доктору {state.selected_slot['doctor_name']}"
        )

    def _get_or_create_state(
        self, session_id: str, phone: str | None
    ) -> BookingState:
        state = BOOKING_SESSIONS.get(session_id)

        if state is None:
            state = BookingState(session_id=session_id, phone=phone)
            BOOKING_SESSIONS[session_id] = state

        if phone and not state.phone:
            state.phone = phone

        return state

    def _response(
        self,
        state: BookingState,
        answer: str,
    ) -> AgentChatResponse:
        return AgentChatResponse(session_id=state.session_id, answer=answer)
