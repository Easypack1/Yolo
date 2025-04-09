# 나라+항공사별 규정
POLICIES = {
    "일본_대한항공": {
        "knife": "반입 불가",
        "scissors": "반입 불가",
        "laptop": "기내 반입 가능",
        "bottle": "위탁 가능",
        "power_bank": "기내 반입 가능",
        "dog": "위탁 가능",
        "cat": "위탁 가능",
        "spray": "반입 불가",
        "hammer": "반입 불가"
    },
    "일본_티웨이": {
        "knife": "반입 불가",
        "scissors": "반입 불가",
        "laptop": "기내 반입 가능",
        "bottle": "기내 반입 가능",
        "power_bank": "기내 반입 불가",
        "dog": "위탁 가능",
        "cat": "위탁 가능",
        "spray": "반입 불가",
        "hammer": "반입 불가"
    },
    "미국_대한항공": {
        "knife": "반입 불가",
        "scissors": "반입 불가",
        "laptop": "기내 반입 가능",
        "bottle": "기내 반입 불가",
        "power_bank": "기내 반입 가능",
        "dog": "위탁 가능",
        "cat": "위탁 가능",
        "spray": "반입 불가",
        "hammer": "반입 불가"
    },
    "태국_제주항공": {
        "knife": "반입 불가",
        "scissors": "반입 불가",
        "laptop": "기내 반입 가능",
        "bottle": "기내 반입 가능",
        "power_bank": "위탁 불가",
        "dog": "위탁 가능",
        "cat": "기내 반입 가능",
        "spray": "반입 불가",
        "hammer": "반입 불가"
    },
    # ... 계속 추가 가능 ...
}

def get_policy(travel_destination: str, airline: str) -> dict:
    key = f"{travel_destination}_{airline}"
    return POLICIES.get(key, {})
