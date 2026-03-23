"""Subscription plan definitions based on PRD Section 4."""

import enum


class PlanTier(str, enum.Enum):
    FREEMIUM = "freemium"
    BASIC = "basic"
    PRO = "pro"
    PREMIUM = "premium"


# Plan limits and features per tier
PLAN_DEFINITIONS: dict[str, dict] = {
    PlanTier.FREEMIUM: {
        "max_companies": 0,
        "max_products_per_company": 0,
        "max_members_per_company": 0,
        "can_create_company": False,
        "can_apply": False,
        "has_dezzcovery": True,
        "has_dezzviewer": False,
        "has_human_review": False,
    },
    PlanTier.BASIC: {
        "max_companies": 1,
        "max_products_per_company": 3,
        "max_members_per_company": 3,
        "can_create_company": True,
        "can_apply": True,
        "has_dezzcovery": True,
        "has_dezzviewer": False,
        "has_human_review": False,
    },
    PlanTier.PRO: {
        "max_companies": 2,
        "max_products_per_company": 3,
        "max_members_per_company": 3,
        "can_create_company": True,
        "can_apply": True,
        "has_dezzcovery": True,
        "has_dezzviewer": True,
        "has_human_review": False,
    },
    PlanTier.PREMIUM: {
        "max_companies": 2,
        "max_products_per_company": 3,
        "max_members_per_company": 3,
        "can_create_company": True,
        "can_apply": True,
        "has_dezzcovery": True,
        "has_dezzviewer": True,
        "has_human_review": True,
    },
}
