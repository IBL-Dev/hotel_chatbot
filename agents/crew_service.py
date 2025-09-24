def service_flow(user_input: str) -> str:
    """
    Simulated hotel service workflow.
    You can expand with real service APIs later.
    """
    if "spa" in user_input.lower():
        return "Our spa is open from 9 AM to 9 PM. Would you like me to book a session?"
    elif "restaurant" in user_input.lower():
        return "Our restaurant is open 24/7. Do you want to see today’s menu?"
    elif "taxi" in user_input.lower() or "transport" in user_input.lower():
        return "We can arrange transport for you. Please share your destination."
    else:
        return "Service flow started. Please specify the service you need (e.g., spa, restaurant, taxi)."
