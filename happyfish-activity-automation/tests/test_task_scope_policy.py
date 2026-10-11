# -*- coding: utf-8 -*-
"""Dry-run matrix for task_scope_policy; no ADB, MFA or game required."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from task_scope_policy import Proposal, decide  # noqa: E402


class ScopePolicyTests(unittest.TestCase):
    def check(self, expected, **kwargs):
        # Known ownership in normal test cases; dedicated tests cover unknown.
        kwargs.setdefault("maa_ownership_verified", True)
        kwargs.setdefault("feature_id", "unrelated-event")
        outcome = decide(Proposal(**kwargs))
        self.assertEqual(outcome.allowed, expected, outcome.reason)
        return outcome.reason

    def test_default_no_scope_no_mode(self):
        self.check(False, mode="daily", scope="none", action="gameplay")
        self.check(False, mode="unknown", scope="assigned", action="gameplay")

    def test_maa_daily_off_or_not_run_does_not_authorize_agent(self):
        self.assertEqual(
            self.check(False, mode="daily", scope="assigned", action="gameplay",
                       maa_owned=True, activity_verified=True, resource="none"),
            "maa_owns_task_even_if_off_or_not_run",
        )

    def test_maa_failure_not_automatic_fallback(self):
        self.check(False, mode="daily", scope="assigned", action="maa_recovery",
                   maa_owned=True, maa_failure_verified=True, retry_no_duplicate=True)
        self.check(False, mode="daily", scope="assigned", action="maa_recovery",
                   maa_owned=True, fallback_authorized=True, retry_no_duplicate=True)
        self.check(False, mode="daily", scope="assigned", action="maa_recovery",
                   maa_owned=True, fallback_authorized=True, maa_failure_verified=True)

    def test_maa_fallback_requires_every_gate(self):
        self.check(True, mode="daily", scope="assigned", action="maa_recovery",
                   maa_owned=True, fallback_authorized=True, maa_failure_verified=True,
                   retry_no_duplicate=True)
        self.check(False, mode="daily", scope="assigned", action="maa_recovery",
                   maa_owned=True, fallback_authorized=True, maa_failure_verified=True,
                   retry_no_duplicate=True, maa_busy=True)

    def test_discovery_not_execution_even_if_button_is_free(self):
        self.check(True, mode="feature", scope="discovery", action="observe", maa_owned=True)
        self.check(False, mode="feature", scope="discovery", action="gameplay",
                   gameplay_authorized=True, activity_verified=True, resource="A")

    def test_feature_named_but_without_permission_to_spend_one_free_attempt(self):
        self.check(False, mode="feature", scope="assigned", action="gameplay",
                   activity_verified=True, resource="A")
        self.check(True, mode="feature", scope="assigned", action="gameplay",
                   gameplay_authorized=True, activity_verified=True, resource="A")

    def test_daily_authorized_free_play_is_allowed(self):
        self.check(True, mode="daily", scope="assigned", action="gameplay",
                   activity_verified=True, resource="A")
        self.check(True, mode="daily", scope="assigned", action="gameplay",
                   activity_verified=True, resource="B")

    def test_not_verified_activity_is_blocked(self):
        self.check(False, mode="daily", scope="assigned", action="gameplay", resource="A")

    def test_final_reward_selection_remains_user_owned(self):
        self.check(False, mode="daily", scope="assigned", action="final_redeem",
                   activity_verified=True, resource="C")
        self.check(False, mode="daily", scope="assigned", action="final_redeem",
                   activity_verified=True, resource="C", final_choice_authorized=True)
        self.check(True, mode="daily", scope="assigned", action="final_redeem",
                   activity_verified=True, resource="C", final_choice_authorized=True,
                   final_reward_item="图纸", final_reward_quantity=1)
        self.check(False, mode="daily", scope="assigned", action="final_redeem",
                   activity_verified=False, resource="C", final_choice_authorized=True,
                   final_reward_item="图纸", final_reward_quantity=1)

    def test_inappropriate_paid_persistent_unknown_blocked(self):
        for resource in ("D", "E", "unknown"):
            with self.subTest(resource=resource):
                self.check(False, mode="daily", scope="assigned", action="gameplay",
                           activity_verified=True, resource=resource)

    def test_maa_independent_feature_is_still_maa_owned(self):
        self.check(False, mode="feature", scope="assigned", action="gameplay",
                   maa_owned=True, gameplay_authorized=True, activity_verified=True, resource="A")

    def test_work_in_progress_maa_prevents_clicks(self):
        self.check(False, mode="daily", scope="assigned", action="gameplay",
                   resource="A", activity_verified=True, maa_busy=True)

    def test_scope_does_not_grant_maa_repo_changes(self):
        self.check(False, mode="feature", scope="assigned", action="modify_code",
                   code_change_authorized=True, target_maa_repo=True)
        self.check(True, mode="feature", scope="assigned", action="modify_code",
                   code_change_authorized=True, target_maa_repo=False)

    def test_missing_maa_ownership_check_is_never_permission(self):
        self.assertEqual(
            self.check(False, mode="daily", scope="assigned", action="gameplay",
                       activity_verified=True, resource="A", maa_ownership_verified=False),
            "maa_ownership_not_verified",
        )
        self.check(False, mode="daily", scope="assigned", action="final_redeem",
                   activity_verified=True, resource="C", final_choice_authorized=True,
                   final_reward_item="金币", final_reward_quantity=1,
                   maa_ownership_verified=False)
        self.check(False, mode="daily", scope="assigned", action="maa_recovery",
                   maa_owned=True, fallback_authorized=True, maa_failure_verified=True,
                   retry_no_duplicate=True, maa_ownership_verified=False)

    def test_final_reward_needs_specific_item_and_valid_quantity(self):
        self.check(False, mode="daily", scope="assigned", action="final_redeem",
                   resource="C", activity_verified=True, final_choice_authorized=True,
                   final_reward_item="金币", final_reward_quantity=0)
        self.check(False, mode="daily", scope="assigned", action="final_redeem",
                   resource="C", activity_verified=True, final_choice_authorized=True,
                   final_reward_item="金币", final_reward_quantity=-1)
        self.check(False, mode="daily", scope="assigned", action="final_redeem",
                   resource="C", activity_verified=True, final_choice_authorized=True,
                   final_reward_item="金币", final_reward_quantity=True)

    def test_puzzle_numbering_is_explicit_offline_only(self):
        self.check(False, mode="daily", scope="assigned", action="puzzle_numbering",
                   puzzle_image_available=True)
        self.check(False, mode="feature", scope="discovery", action="puzzle_numbering",
                   puzzle_image_available=True)
        self.check(False, mode="feature", scope="assigned", action="puzzle_numbering")
        self.assertEqual(
            self.check(True, mode="feature", scope="assigned", action="puzzle_numbering",
                       puzzle_image_available=True, maa_owned=True,
                       maa_ownership_verified=False, maa_busy=True),
            "picture_analysis_only_no_game_or_maa_actions",
        )
        self.check(False, mode="feature", scope="assigned", action="gameplay",
                   maa_owned=True, maa_ownership_verified=True,
                   activity_verified=True, gameplay_authorized=True, resource="A")

    def test_wishing_lamp_requires_explicit_permission_even_if_labeled_free(self):
        for mode in ("daily", "feature"):
            with self.subTest(mode=mode):
                self.assertEqual(
                    self.check(False, mode=mode, scope="assigned", action="navigate",
                               feature_id="许愿神灯", activity_verified=True),
                    "wishing_lamp_explicit_user_authorization_required",
                )
                self.check(False, mode=mode, scope="assigned", action="gameplay",
                           feature_id="wishing-lamp", resource="A", activity_verified=True,
                           gameplay_authorized=True)

    def test_wishing_lamp_view_permission_cannot_spend_any_silk(self):
        self.assertEqual(
            self.check(True, mode="feature", scope="assigned", action="navigate",
                       feature_id="wishing_lamp", special_feature_authorized=True),
            "explicit_wishing_lamp_view_only",
        )
        self.assertEqual(
            self.check(False, mode="feature", scope="assigned", action="gameplay",
                       feature_id="许愿神灯", resource="D", activity_verified=True,
                       gameplay_authorized=True, special_feature_authorized=True),
            "wishing_lamp_spend_not_authorized",
        )

    def test_wishing_lamp_explicit_silk_type_and_count_required(self):
        base = dict(mode="feature", scope="assigned", action="gameplay",
                    feature_id="wishing-lamp", activity_verified=True,
                    special_feature_authorized=True, wishing_lamp_spend_authorized=True,
                    gameplay_authorized=True, resource="D")
        self.check(False, **base)
        self.check(False, **dict(base, wishing_lamp_resource="regular"))
        self.check(False, **dict(base, wishing_lamp_resource="regular", wishing_lamp_max_uses=0))
        self.check(False, **dict(base, wishing_lamp_resource="gold", wishing_lamp_max_uses=True))
        self.assertEqual(
            self.check(True, **dict(base, wishing_lamp_resource="regular", wishing_lamp_max_uses=2)),
            "wishing_lamp_bounded_user_instruction_preview_only",
        )
        self.check(True, **dict(base, wishing_lamp_resource="gold", wishing_lamp_max_uses=1))

    def test_wishing_lamp_maa_fallback_is_not_a_special_permission(self):
        self.check(False, mode="daily", scope="assigned", action="maa_recovery",
                   feature_id="擦神灯", maa_owned=True,
                   fallback_authorized=True, maa_failure_verified=True,
                   retry_no_duplicate=True)
        self.check(False, mode="feature", scope="discovery", action="navigate",
                   feature_id="wishing-lamp", special_feature_authorized=True)
        self.assertEqual(
            self.check(False, mode="feature", scope="assigned", action="navigate",
                       feature_id="wishing-lamp", special_feature_authorized=True,
                       maa_ownership_verified=False),
            "maa_ownership_not_verified",
        )

    def test_wishing_lamp_generic_maa_recovery_or_final_redeem_is_blocked(self):
        self.assertEqual(
            self.check(False, mode="feature", scope="assigned", action="maa_recovery",
                       feature_id="wishing-lamp", special_feature_authorized=True,
                       maa_owned=True, fallback_authorized=True,
                       maa_failure_verified=True, retry_no_duplicate=True),
            "wishing_lamp_maa_recovery_requires_separate_review",
        )
        self.assertEqual(
            self.check(False, mode="feature", scope="assigned", action="final_redeem",
                       feature_id="许愿神灯", special_feature_authorized=True,
                       resource="C", activity_verified=True, gameplay_authorized=True,
                       final_choice_authorized=True, final_reward_item="金币",
                       final_reward_quantity=1),
            "wishing_lamp_unmodeled_redemption_is_not_authorized",
        )

    def test_mutating_game_action_needs_identified_feature(self):
        self.assertEqual(
            self.check(False, mode="daily", scope="assigned", action="navigate",
                       feature_id=""),
            "feature_identity_not_supplied",
        )
        self.check(False, mode="daily", scope="assigned", action="gameplay",
                   feature_id="", activity_verified=True, resource="A")
        self.check(True, mode="feature", scope="discovery", action="observe",
                   feature_id="")

    def test_no_random_unknown_action(self):
        self.check(False, mode="daily", scope="assigned", action="clear_red_dots")


if __name__ == "__main__":
    unittest.main()
