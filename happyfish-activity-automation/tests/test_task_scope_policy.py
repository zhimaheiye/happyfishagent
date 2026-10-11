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

    def test_no_random_unknown_action(self):
        self.check(False, mode="daily", scope="assigned", action="clear_red_dots")


if __name__ == "__main__":
    unittest.main()
