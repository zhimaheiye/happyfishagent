# -*- coding: utf-8 -*-
"""Pure offline policy preview for Agent planning. No input-device control.

IMPORTANT: A caller supplies the facts here. This function does not verify OCR,
user consent, MAA logs or actual game state; it is NOT a runtime security gate.
Normative text: references/agent-work-modes-maa-boundary.md.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Proposal:
    mode: str                      # daily | feature
    scope: str                     # assigned | discovery | none
    action: str                    # observe | puzzle_numbering | navigate | gameplay | order_fish | friend_mail | final_redeem | maa_recovery | modify_code
    feature_id: str = ""           # required for game navigation/operation; 'wishing-lamp' is ALWAYS excluded
    maa_owned: bool = False        # True = current substep is MAA-owned; false alone is NOT proof
    maa_ownership_verified: bool = False  # must check latest MAA substeps/independent/global routes
    maa_busy: bool = False         # MFA / person actively using simulator
    puzzle_image_available: bool = False  # already supplied/specified; never fetch via game clicks
    resource: str = "none"         # none | A | B | C | D | E | unknown
    activity_verified: bool = False
    gameplay_authorized: bool = False  # feature mode must explicitly allow real actions
    order_fish_authorized: bool = False  # existing user authorization, only verified order juveniles
    order_fish_matches: bool = False  # order species and fish panel checked
    order_fish_juvenile: bool = False  # all selected fish juveniles; not crowns / gene-bearing
    order_fish_count_matches: bool = False  # selected N = required M > 0
    friend_mail_authorized: bool = False  # handoff to MAA not yet accepted
    friend_mail_category: str = ""   # known action type, never inferred from red dot
    friend_mail_button_verified: bool = False  # same-row OCR/button/bbox confirmed
    final_choice_authorized: bool = False
    final_reward_item: str = ""    # specific reward selected by user, not a model choice
    final_reward_quantity: int = 0
    fallback_authorized: bool = False
    maa_failure_verified: bool = False
    retry_no_duplicate: bool = False
    code_change_authorized: bool = False
    target_maa_repo: bool = False


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str


def _canonical_feature(value: str) -> str:
    name = (value or "").strip().lower().replace("_", "-")
    if name in {"wishing-lamp", "wishinglamp", "wish-lamp", "许愿神灯", "擦神灯", "许愿绸", "许愿金绸", "神灯", "幸运神灯"}:
        return "wishing-lamp"
    if "许愿神灯" in name or "幸运神灯" in name:
        return "wishing-lamp"
    if name in {"gem-order", "gemorder", "gemordertask", "gem-order-task",
                "宝石订单", "宝石订单气泡", "订单未完成"}:
        return "gem-order"
    if "宝石订单" in name or ("订单" in name and "未完成" in name):
        return "gem-order"
    if name in {"mijing-order-fish", "秘境之门订单鱼", "秘境之门", "订单送鱼"}:
        return "mijing-order-fish"
    if name in {"friend-mail", "好友留言", "好友消息", "留言箱"}:
        return "friend-mail"
    return name


def decide(p: Proposal) -> Decision:
    """Fail-closed preview; output is advisory and cannot authorize live clicks."""
    deny = lambda msg: Decision(False, msg)
    allow = lambda msg: Decision(True, msg)

    if p.mode not in {"daily", "feature"}:
        return deny("no_valid_mode")
    if p.scope not in {"assigned", "discovery", "none"}:
        return deny("invalid_scope")
    if p.action not in {"observe", "puzzle_numbering", "navigate", "gameplay", "order_fish", "friend_mail", "final_redeem", "maa_recovery", "modify_code"}:
        return deny("unknown_action")
    if p.scope == "none":
        return deny("not_in_user_scope")
    if p.action == "observe":
        return allow("read_only_within_discovery_or_assignment")
    if p.action == "puzzle_numbering":
        # Offline picture analysis is separate from operating MAA's puzzle.
        if p.mode != "feature" or p.scope != "assigned":
            return deny("puzzle_numbering_only_on_user_request")
        if not p.puzzle_image_available:
            return deny("puzzle_image_required_no_game_navigation")
        return allow("picture_analysis_only_no_game_or_maa_actions")

    # From here the action can change real state.
    feature = _canonical_feature(p.feature_id)
    if p.action in {"navigate", "gameplay", "order_fish", "friend_mail", "final_redeem", "maa_recovery"}:
        if not feature:
            return deny("feature_identity_not_supplied")
        if feature == "wishing-lamp":
            # User transferred ALL real game operation for this feature to MaaHappyFish.
            # No Agent-side grant or 'read only navigation' may override this deny.
            return deny("wishing_lamp_owned_by_maa_agent_prohibited")
        if feature == "gem-order" and p.action != "maa_recovery":
            # A pending-order bubble is NOT user authorization or proof of MAA failure.
            # Deny entering, manipulating and redeeming regardless of claimed maa_owned.
            return deny("gem_order_maa_owned_bubble_not_a_task")

    if p.scope != "assigned":
        return deny("discovery_is_read_only")
    if p.maa_busy:
        return deny("simulator_or_maa_busy")
    if p.action in {"navigate", "gameplay", "order_fish", "friend_mail", "final_redeem", "maa_recovery"} and not p.maa_ownership_verified:
        return deny("maa_ownership_not_verified")

    if p.action == "order_fish":
        # Specific exception: current user authorized delivering verified order juveniles.
        # A resource-D exception is never a license to sell/free-send arbitrary fish.
        if feature != "mijing-order-fish" or not p.order_fish_authorized:
            return deny("order_fish_specific_authorization_required")
        if not p.activity_verified or not (
            p.order_fish_matches and p.order_fish_juvenile and p.order_fish_count_matches
        ):
            return deny("order_fish_identity_juvenile_count_not_verified")
        return allow("verified_order_juveniles_only_preview")
    if p.action == "friend_mail":
        # MAA has code but user has not tested/handover; this bounded Agent duty remains.
        if feature != "friend-mail" or not p.friend_mail_authorized:
            return deny("friend_mail_current_assignment_required")
        if p.friend_mail_category not in {"friend_request_accept", "baby_visit_ignore", "system_notice_delete"}:
            return deny("friend_mail_unknown_category")
        if not p.friend_mail_button_verified:
            return deny("friend_mail_per_row_ocr_required")
        return allow("known_friend_message_action_preview")
    if p.action == "maa_recovery":
        # Specific GemOrderTask recoveries may be considered only if MAA ownership
        # is correctly verified, user approves, and genuine failure & idempotency pass.
        if not p.maa_owned:
            return deny("not_a_maa_recovery_target")
        if not p.fallback_authorized:
            return deny("fallback_not_authorized")
        if not p.maa_failure_verified:
            return deny("no_verified_failure")
        if not p.retry_no_duplicate:
            return deny("retry_might_repeat_side_effect")
        return allow("bounded_maa_fallback_only")

    if p.action == "modify_code":
        if not p.code_change_authorized:
            return deny("code_changes_not_authorized")
        if p.target_maa_repo:
            # Separate user authorization for changes to MaaHappyFish must be
            # handled by its own development workflow, outside this preview.
            return deny("maa_stable_code_requires_separate_development_approval")
        return allow("scoped_non_maa_code_change")

    if p.maa_owned:
        return deny("maa_owns_task_even_if_off_or_not_run")
    if p.action == "navigate":
        return allow("authorized_navigation")
    if p.mode == "feature" and not p.gameplay_authorized:
        return deny("feature_inspection_does_not_authorize_gameplay")
    if p.resource in {"unknown", "D", "E"}:
        return deny("unknown_or_persistent_or_paid_resource")

    if p.action == "final_redeem":
        if p.resource != "C" or not p.activity_verified:
            return deny("not_a_verified_final_reward_action")
        if not p.final_choice_authorized:
            return deny("user_must_choose_final_reward")
        if not p.final_reward_item.strip() or type(p.final_reward_quantity) is not int or p.final_reward_quantity < 1:
            return deny("final_reward_item_and_quantity_required")
        return allow("user_selected_specific_final_reward")

    if p.action == "gameplay":
        if p.resource not in {"none", "A", "B"}:
            return deny("not_a_free_in_activity_action")
        if not p.activity_verified:
            return deny("activity_identity_not_verified")
        return allow("authorized_non_maa_activity_step")

    return deny("unexpected_case")


if __name__ == "__main__":
    print("Offline helper only; run: python -m unittest discover -s happyfish-activity-automation/tests -p 'test_*.py'")
