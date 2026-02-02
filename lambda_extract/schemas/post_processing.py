def post_additional_sessions(agreement: dict) -> dict:
    single_payment = agreement.get("payment")

    agreement["payment"] = {
        "scholarship_payment": None,
        "multiple_payment": None,
        "single_payment": single_payment,
    }

    agreement["services"] = [agreement["services"]]
    return agreement


def post_skill_building(agreement: dict) -> dict:
    agreement["payment"] = {
        "scholarship_payment": None,
        "multiple_payment": None,
        "single_payment": {
            "amount": agreement["total_tuition"],
        },
    }
    return agreement


def post_tutoring(agreement: dict) -> dict:
    agreement["payment"] = {
        "scholarship_payment": None,
        "multiple_payment": None,
        "single_payment": {
            "amount": agreement["services"]["tuition"],
        },
    }

    agreement["one_to_one_sessions"] = agreement["services"]["units"]
    agreement["services"] = [agreement["services"]]
    return agreement
