import httpx
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="TripMate AI",
    page_icon="✈️",
    layout="wide",
)


# -----------------------------------
# Session state
# -----------------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if "backend_notified" not in st.session_state:
    st.session_state.backend_notified = False

if "trip_result" not in st.session_state:
    st.session_state.trip_result = None

if "selected_saved_trip" not in st.session_state:
    st.session_state.selected_saved_trip = None


# -----------------------------------
# Backend health check
# -----------------------------------

def check_backend() -> bool:

    try:

        response = httpx.get(
            f"{API_BASE_URL}/health",
            timeout=5.0,
        )

        response.raise_for_status()

        return (
            response.json().get("status")
            == "healthy"
        )

    except (
        httpx.RequestError,
        httpx.HTTPStatusError,
    ):
        return False


def get_error_detail(
    response: httpx.Response,
    default_message: str,
) -> str:

    try:

        data = response.json()

        return data.get(
            "detail",
            default_message,
        )

    except ValueError:

        return default_message


# -----------------------------------
# Trip history helpers
# -----------------------------------

def get_trip_history(
    user_id: int,
) -> tuple[list[dict], str | None]:

    try:

        response = httpx.get(
            (
                f"{API_BASE_URL}"
                f"/trips/history/{user_id}"
            ),
            timeout=10.0,
        )

        if response.status_code != 200:

            return (
                [],
                get_error_detail(
                    response,
                    "Unable to load trip history.",
                ),
            )

        data = response.json()

        return (
            data.get("trips", []),
            None,
        )

    except httpx.TimeoutException:

        return (
            [],
            "Trip history request timed out.",
        )

    except httpx.RequestError:

        return (
            [],
            "Unable to connect to TripMate backend.",
        )


def get_saved_trip(
    trip_id: int,
) -> tuple[dict | None, str | None]:

    try:

        response = httpx.get(
            (
                f"{API_BASE_URL}"
                f"/trips/{trip_id}"
            ),
            timeout=10.0,
        )

        if response.status_code != 200:

            return (
                None,
                get_error_detail(
                    response,
                    "Unable to load saved trip.",
                ),
            )

        return (
            response.json(),
            None,
        )

    except httpx.TimeoutException:

        return (
            None,
            "Saved trip request timed out.",
        )

    except httpx.RequestError:

        return (
            None,
            "Unable to connect to TripMate backend.",
        )


backend_available = check_backend()


if not st.session_state.backend_notified:

    if backend_available:

        st.toast(
            "Backend connected",
            icon="✅",
        )

    else:

        st.toast(
            "Backend unavailable",
            icon="⚠️",
        )

    st.session_state.backend_notified = True


# -----------------------------------
# Header
# -----------------------------------

st.title(
    "✈️ TripMate AI"
)

st.caption(
    "Agentic AI Travel Planning Assistant"
)


# -----------------------------------
# Sidebar
# -----------------------------------

with st.sidebar:

    st.header(
        "👤 Account"
    )

    if st.session_state.user is None:

        account_mode = st.radio(
            "Choose an option",
            [
                "Existing User",
                "Create Account",
            ],
        )

        # -------------------------------
        # Existing user
        # -------------------------------

        if account_mode == "Existing User":

            email = st.text_input(
                "Email",
                placeholder="you@example.com",
            )

            if st.button(
                "Continue",
                use_container_width=True,
            ):

                if not email:

                    st.warning(
                        "Enter your email."
                    )

                else:

                    try:

                        response = httpx.get(
                            (
                                f"{API_BASE_URL}"
                                "/users/by-email"
                            ),
                            params={
                                "email": email.strip()
                            },
                            timeout=10.0,
                        )


                        if response.status_code == 404:

                            st.error(
                                "No account was found with this email."
                            )


                        elif response.status_code != 200:

                            st.error(
                                get_error_detail(
                                    response,
                                    "Unable to retrieve user.",
                                )
                            )


                        else:

                            st.session_state.user = (
                                response.json()
                            )

                            st.session_state.trip_result = None
                            st.session_state.selected_saved_trip = None

                            st.rerun()

                    except httpx.RequestError:

                        st.error(
                            "Unable to connect "
                            "to TripMate backend."
                        )

        # -------------------------------
        # New user
        # -------------------------------

        else:

            name = st.text_input(
                "Name",
                placeholder="Your name",
            )

            email = st.text_input(
                "Email",
                placeholder="you@example.com",
                key="new_user_email",
            )

            if st.button(
                "Create Account",
                use_container_width=True,
            ):

                if not name or not email:

                    st.warning(
                        "Enter your name and email."
                    )

                else:

                    try:

                        response = httpx.post(
                            f"{API_BASE_URL}/users",
                            json={
                                "name": name.strip(),
                                "email": email.strip(),
                            },
                            timeout=10.0,
                        )


                        if response.status_code == 409:

                            st.error(
                                "An account with this email already exists."
                            )


                        elif response.status_code != 201:

                            st.error(
                                get_error_detail(
                                    response,
                                    "Unable to create account.",
                                )
                            )


                        else:

                            st.session_state.user = (
                                response.json()
                            )

                            st.session_state.trip_result = None
                            st.session_state.selected_saved_trip = None

                            st.toast(
                                "Account created",
                                icon="✅",
                            )

                            st.rerun()

                    except httpx.RequestError:

                        st.error(
                            "Unable to connect "
                            "to TripMate backend."
                        )

    else:

        user = st.session_state.user

        st.write(
            f"### 👋 {user['name']}"
        )

        st.caption(
            user["email"]
        )

        if st.button(
            "Switch User",
            use_container_width=True,
        ):

            st.session_state.user = None
            st.session_state.trip_result = None
            st.session_state.selected_saved_trip = None

            st.rerun()

        st.divider()

        # -----------------------------------
        # Trip history
        # -----------------------------------

        st.subheader(
            "🧳 Previous Trips"
        )

        trip_history, history_error = (
            get_trip_history(
                user_id=user["id"]
            )
        )

        if history_error:

            st.warning(
                history_error
            )

        elif not trip_history:

            st.caption(
                "No previous trips yet."
            )

        else:

            for trip in trip_history:

                destination = (
                    trip.get("destination")
                    or "Unknown destination"
                )

                start_date = trip.get(
                    "start_date"
                )

                end_date = trip.get(
                    "end_date"
                )

                trip_id = trip.get(
                    "id"
                )

                st.write(
                    f"**📍 {destination}**"
                )

                if start_date and end_date:

                    st.caption(
                        f"{start_date} → {end_date}"
                    )

                elif start_date:

                    st.caption(
                        start_date
                    )

                if st.button(
                    "View Trip",
                    key=f"history_trip_{trip_id}",
                    use_container_width=True,
                ):

                    saved_trip, trip_error = (
                        get_saved_trip(
                            trip_id=trip_id
                        )
                    )

                    if trip_error:

                        st.error(
                            trip_error
                        )

                    elif saved_trip:

                        st.session_state.selected_saved_trip = (
                            saved_trip
                        )

                        st.rerun()

                st.divider()


# -----------------------------------
# Main area
# -----------------------------------

if st.session_state.user is None:

    st.subheader(
        "Welcome to TripMate"
    )

    st.write(
        "Select or create an account "
        "from the sidebar to continue."
    )

else:

    user = st.session_state.user

    st.subheader(
        f"Welcome, {user['name']} 👋"
    )

    st.caption(
        "Tell TripMate where you want to go "
        "and let the AI agents plan your journey."
    )

    st.divider()

    # -----------------------------------
    # Selected saved trip
    # -----------------------------------

    if st.session_state.selected_saved_trip:

        saved_trip = (
            st.session_state.selected_saved_trip
        )

        st.subheader(
            "🧳 Previous Trip"
        )

        destination = (
            saved_trip.get("destination")
            or "Unknown destination"
        )

        origin = (
            saved_trip.get("origin")
            or "Unknown origin"
        )

        st.write(
            f"### {origin} → {destination}"
        )

        start_date = saved_trip.get(
            "start_date"
        )

        end_date = saved_trip.get(
            "end_date"
        )

        if start_date and end_date:

            st.caption(
                f"📅 {start_date} → {end_date}"
            )

        adults = saved_trip.get(
            "adults"
        )

        children = saved_trip.get(
            "children"
        )

        budget = saved_trip.get(
            "budget"
        )

        info_col1, info_col2, info_col3 = (
            st.columns(3)
        )

        with info_col1:

            st.metric(
                "Adults",
                adults
                if adults is not None
                else "—",
            )

        with info_col2:

            st.metric(
                "Children",
                children
                if children is not None
                else "—",
            )

        with info_col3:

            st.metric(
                "Budget",
                (
                    f"{budget}"
                    if budget is not None
                    else "—"
                ),
            )

        original_query = saved_trip.get(
            "user_query"
        )

        if original_query:

            with st.expander(
                "Original Request"
            ):

                st.write(
                    original_query
                )

        itinerary = saved_trip.get(
            "itinerary"
        )

        final_response = saved_trip.get(
            "final_response"
        )

        if itinerary:

            st.markdown(
                "### 🗓️ Saved Itinerary"
            )

            st.markdown(
                itinerary
            )

        elif final_response:

            st.markdown(
                "### 🤖 Saved Response"
            )

            st.markdown(
                final_response
            )

        if st.button(
            "Close Previous Trip"
        ):

            st.session_state.selected_saved_trip = None

            st.rerun()

        st.divider()


    # -----------------------------------
    # Trip planning interface
    # -----------------------------------

    st.subheader(
        "🌍 Plan Your Trip"
    )

    trip_query = st.text_area(
        "Describe your trip",
        height=180,
        placeholder=(
            "Example: Plan a trip to Jeddah, Saudi Arabia. "
            "Search for flights from BOM to JED on 2026-10-10. "
            "Find hotels from 2026-10-10 to 2026-10-15 "
            "for 2 adults, check the weather, find tourist "
            "attractions, and create a complete itinerary."
        ),
    )

    st.caption(
        "Include your destination, dates, travelers, "
        "and the services you need for better results."
    )

    plan_trip = st.button(
        "✈️ Plan My Trip",
        type="primary",
        use_container_width=True,
        disabled=not backend_available,
    )

    if plan_trip:

        if not backend_available:

            st.toast(
                "TripMate backend is unavailable.",
                icon="⚠️",
            )

        elif not trip_query.strip():

            st.warning(
                "Please describe your trip first."
            )

        else:

            with st.spinner(
                "TripMate agents are planning your trip..."
            ):

                try:

                    response = httpx.post(
                        f"{API_BASE_URL}/trips/plan",
                        json={
                            "user_id": user["id"],
                            "user_query": trip_query.strip(),
                        },
                        timeout=180.0,
                    )

                    if response.status_code != 200:

                        st.error(
                            get_error_detail(
                                response,
                                "Trip planning failed.",
                            )
                        )

                    else:

                        st.session_state.trip_result = (
                            response.json()
                        )

                        st.session_state.selected_saved_trip = None

                        st.toast(
                            "Trip plan generated successfully",
                            icon="✅",
                        )

                        st.rerun()

                except httpx.TimeoutException:

                    st.error(
                        "Trip planning took too long. "
                        "Please try again."
                    )

                except httpx.RequestError:

                    st.error(
                        "Unable to connect to "
                        "TripMate backend."
                    )


    # -----------------------------------
    # Temporary result confirmation
    # -----------------------------------

    if st.session_state.trip_result:

        result = st.session_state.trip_result

        st.divider()

        st.subheader(
            "🧭 Your Trip Plan"
        )

        # -----------------------------------
        # Small workflow summary
        # -----------------------------------

        required_agents = result.get(
            "required_agents",
            [],
        )

        completed_agents = result.get(
            "completed_agents",
            [],
        )

        failed_agents = result.get(
            "failed_agents",
            [],
        )

        col1, col2, col3 = st.columns(
            3
        )

        with col1:

            st.metric(
                "Agents Selected",
                len(required_agents),
            )

        with col2:

            st.metric(
                "Specialists Completed",
                len(completed_agents),
            )

        with col3:

            st.metric(
                "Failed",
                len(failed_agents),
            )

        # -----------------------------------
        # Specialist results
        # -----------------------------------

        st.subheader(
            "🔎 Travel Information"
        )

        flight_result = result.get(
            "flight_result"
        )

        hotel_result = result.get(
            "hotel_result"
        )

        weather_result = result.get(
            "weather_result"
        )

        places_result = result.get(
            "places_result"
        )


        # Flight
        if flight_result:

            with st.expander(
                "✈️ Flights",
                expanded=True,
            ):

                st.markdown(
                    flight_result.get(
                        "answer",
                        "No flight information available.",
                    )
                )

                tools = flight_result.get(
                    "tools_used",
                    [],
                )

                if tools:

                    st.caption(
                        "Tool used: "
                        + ", ".join(tools)
                    )


        # Hotel
        if hotel_result:

            with st.expander(
                "🏨 Hotels",
                expanded=True,
            ):

                st.markdown(
                    hotel_result.get(
                        "answer",
                        "No hotel information available.",
                    )
                )

                tools = hotel_result.get(
                    "tools_used",
                    [],
                )

                if tools:

                    st.caption(
                        "Tool used: "
                        + ", ".join(tools)
                    )


        # Weather
        if weather_result:

            with st.expander(
                "🌤️ Weather",
                expanded=False,
            ):

                st.markdown(
                    weather_result.get(
                        "answer",
                        "No weather information available.",
                    )
                )

                tools = weather_result.get(
                    "tools_used",
                    [],
                )

                if tools:

                    st.caption(
                        "Tool used: "
                        + ", ".join(tools)
                    )


        # Places
        if places_result:

            with st.expander(
                "📍 Places & Attractions",
                expanded=False,
            ):

                st.markdown(
                    places_result.get(
                        "answer",
                        "No places information available.",
                    )
                )

                tools = places_result.get(
                    "tools_used",
                    [],
                )

                if tools:

                    st.caption(
                        "Tool used: "
                        + ", ".join(tools)
                    )


        # -----------------------------------
        # Itinerary
        # -----------------------------------

        itinerary = result.get(
            "itinerary"
        )

        final_response = result.get(
            "final_response"
        )

        if itinerary:

            st.divider()

            st.subheader(
                "🗓️ Your Itinerary"
            )

            st.markdown(
                itinerary
            )

        elif final_response:

            st.divider()

            st.subheader(
                "🤖 TripMate Response"
            )

            st.markdown(
                final_response
            )


        # -----------------------------------
        # Persistence / memory status
        # -----------------------------------

        st.divider()

        saved_trip_id = result.get(
            "saved_trip_id"
        )

        trip_saved = result.get(
            "trip_saved",
            False,
        )

        memory_loaded = result.get(
            "memory_loaded",
            False,
        )

        status_col1, status_col2 = st.columns(
            2
        )

        with status_col1:

            if memory_loaded:

                st.caption(
                    "🧠 Previous trip memory used"
                )

            else:

                st.caption(
                    "🧠 No previous trip memory used"
                )

        with status_col2:

            if trip_saved and saved_trip_id:

                st.caption(
                    f"💾 Trip saved as #{saved_trip_id}"
                )

            else:

                st.caption(
                    "💾 Trip was not saved"
                )