"""
Regression tests for the action space wiring.

`config/action_mapping.py` used to be dead code: recording, training and
inference each hardcoded their own 29-slot layout. It is now the single source
of truth, which means a change in one place can silently invalidate every
trained checkpoint. These tests lock the layout that already shipped, so a
future refactor has to say out loud that it is breaking compatibility.

The expectations below were taken from the pre-wiring code, not from the
current implementation. If a test here fails, either the layout genuinely
changed (breaking old checkpoints) or the wiring drifted.
"""

import pytest


# The literal list that shipped in test_model.py before the action space was
# wired in. Action index N in a trained model still means this string.
LEGACY_ACTION_NAMES = [
    "straight",
    "reverse",
    "left",
    "right",
    "forward+left",
    "forward+right",
    "reverse+left",
    "reverse+right",
    "nokeys",
    "LT",
    "RT",
    "Lx",
    "Ly",
    "Rx",
    "Ry",
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT",
    "START",
    "SELECT",
    "L3",
    "R3",
    "LB",
    "RB",
    "A",
    "B",
    "X",
    "Y",
]

# The elif chain that used to live in collect_data.keys_to_output.


def legacy_keys_to_output(keys):
    """The implementation that shipped before the wiring, verbatim."""
    output = [0] * 9
    for combo, slot in (
        (("W", "A"), 4),
        (("W", "D"), 5),
        (("S", "A"), 6),
        (("S", "D"), 7),
        (("W",), 0),
        (("S",), 1),
        (("A",), 2),
        (("D",), 3),
    ):
        if all(key in keys for key in combo):
            output[slot] = 1
            return output
    output[8] = 1
    return output


# =============================================================================
# Action space layout
# =============================================================================


class TestActionSpaceLayout:
    """The action vector layout that trained checkpoints depend on."""

    def test_standard_space_has_29_slots(self):
        from bot_mmorpg.config.action_mapping import ACTION_SPACE_STANDARD

        assert ACTION_SPACE_STANDARD.num_actions == 29

    def test_slot_8_is_no_keys_not_jump(self):
        """Slot 8 was 'jump' in the action space and 'nokeys' in the pipeline.

        Recording writes "nokeys" there. If the action space ever won this
        argument, every trained model would jump constantly.
        """
        from bot_mmorpg.config.action_mapping import (
            ACTION_SPACE_STANDARD,
            NO_KEY_ACTION_ID,
        )

        slot = ACTION_SPACE_STANDARD.actions[8]
        assert slot.id == NO_KEY_ACTION_ID == 8
        assert slot.display_label() == "nokeys"
        assert not slot.key_binding

    def test_slots_are_numbered_sequentially(self):
        from bot_mmorpg.config.action_mapping import ACTION_SPACE_STANDARD

        assert [a.id for a in ACTION_SPACE_STANDARD.actions] == list(range(29))

    def test_labels_match_the_legacy_names(self):
        from bot_mmorpg.config.action_mapping import ACTION_SPACE_STANDARD

        labels = [a.display_label() for a in ACTION_SPACE_STANDARD.actions]
        assert labels == LEGACY_ACTION_NAMES

    def test_output_type_is_multi(self):
        """train_model.py uses BCEWithLogitsLoss, so a single softmax head
        over 29 classes would contradict the loss function."""
        from bot_mmorpg.config.action_mapping import (
            ACTION_SPACE_BASIC,
            ACTION_SPACE_STANDARD,
        )

        assert ACTION_SPACE_STANDARD.output_type == "multi"
        assert ACTION_SPACE_BASIC.output_type == "multi"

    def test_declared_spaces_validate(self):
        from bot_mmorpg.config.action_mapping import validate_action_spaces

        assert validate_action_spaces() == []

    def test_other_space_sizes_are_unchanged(self):
        from bot_mmorpg.config.action_mapping import (
            ACTION_SPACE_BASIC,
            ACTION_SPACE_COMBAT,
            ACTION_SPACE_EXTENDED,
        )

        assert ACTION_SPACE_BASIC.num_actions == 9
        assert ACTION_SPACE_COMBAT.num_actions == 48
        assert ACTION_SPACE_EXTENDED.num_actions == 73

    def test_only_basic_and_standard_reach_the_pipeline(self):
        """combat/extended are documented but execute_action cannot drive
        them, so they must be folded down to standard rather than used."""
        from bot_mmorpg.config.action_mapping import (
            PIPELINE_SUPPORTED_SPACES,
            get_pipeline_action_space,
        )

        assert PIPELINE_SUPPORTED_SPACES == ("basic", "standard")
        for name in ("basic", "standard"):
            assert get_pipeline_action_space(name).name == name
        for name in ("combat", "extended", "nonsense"):
            assert get_pipeline_action_space(name).name == "standard"

    def test_mouse_output_size(self):
        from bot_mmorpg.config.action_mapping import MOUSE_OUTPUT_SIZE

        assert MOUSE_OUTPUT_SIZE == 10

    def test_movement_actions_list_untouched(self):
        """MOVEMENT_ACTIONS still carries the original 'jump' at slot 8; the
        pipeline spaces are built from KEYBOARD_BASE_ACTIONS instead."""
        from bot_mmorpg.config.action_mapping import MOVEMENT_ACTIONS

        assert len(MOVEMENT_ACTIONS) == 16
        assert MOVEMENT_ACTIONS[8].name == "jump"
        assert MOVEMENT_ACTIONS[8].display_label() == "A"


# =============================================================================
# Recording
# =============================================================================


class TestCollectDataWiring:
    """collect_data.py must record the layout the action space declares."""

    def test_action_space_is_the_standard_one(self):
        from bot_mmorpg.scripts import collect_data

        assert collect_data.ACTION_SPACE.name == "standard"
        assert collect_data.ACTION_SPACE.num_actions == 29

    def test_action_widths(self):
        from bot_mmorpg.scripts import collect_data

        assert collect_data.base_action_count() == 29
        assert collect_data.expected_action_width(False) == 29
        assert collect_data.expected_action_width(True) == 39

    def test_describe_action_space_mentions_every_part(self):
        from bot_mmorpg.scripts import collect_data

        text = collect_data.describe_action_space()
        assert "29 actions" in text
        assert "9 keyboard" in text
        assert "20 gamepad" in text
        assert "10 mouse" in text

    def test_capture_screen_default_matches_the_pipeline(self):
        """test_model.py resizes frames to 480x270 and train_model.py never
        rescales, so a different recording size cannot be consumed."""
        import inspect

        from bot_mmorpg.scripts import collect_data

        default = (
            inspect.signature(collect_data.capture_screen)
            .parameters["target_size"]
            .default
        )
        assert default == collect_data.DEFAULT_TARGET_SIZE == (480, 270)

    @pytest.mark.parametrize(
        "held",
        [
            (),
            ("W",),
            ("S",),
            ("A",),
            ("D",),
            ("W", "A"),
            ("W", "D"),
            ("S", "A"),
            ("S", "D"),
            ("W", "A", "D"),
            ("S", "A", "D"),
            ("W", "A", "Q"),
            ("W", "D", "Shift"),
            ("S", "A", "Shift"),
            ("S", "D", "1"),
            ("Q",),
            ("Shift", "1"),
        ],
    )
    def test_keys_to_output_matches_the_legacy_encoder(self, held):
        from bot_mmorpg.scripts import collect_data

        assert collect_data.keys_to_output(list(held)) == legacy_keys_to_output(
            list(held)
        )

    def test_keys_to_output_always_returns_nine_slots(self):
        from bot_mmorpg.scripts import collect_data

        out = collect_data.keys_to_output(["W", "A"])
        assert len(out) == 9
        assert sum(out) == 1
        assert out[4] == 1

    def test_unknown_keys_fall_through_to_no_keys(self):
        from bot_mmorpg.scripts import collect_data

        out = collect_data.keys_to_output(["F5"])
        assert out[8] == 1

    def test_most_specific_combination_wins(self):
        from bot_mmorpg.scripts import collect_data

        assert collect_data.keys_to_output(["W", "A"])[4] == 1
        assert collect_data.keys_to_output(["W", "A", "Q"])[4] == 1
        assert collect_data.keys_to_output(["S", "D", "1"])[7] == 1

    def test_ambiguous_pairs_keep_the_legacy_priority(self):
        """W+A+D matches both diagonals. The old elif chain picked W+A
        first, and that ordering is part of the recorded data."""
        from bot_mmorpg.scripts import collect_data

        assert collect_data.keys_to_output(["W", "A", "D"])[4] == 1
        assert collect_data.keys_to_output(["S", "A", "D"])[6] == 1


# =============================================================================
# Mouse block
# =============================================================================


class TestMouseBlock:
    """The recorded mouse slots and the [0, 1] range they are stored in.

    The block used to be six values (x, y, lmb, rmb, mmb, scroll) written raw.
    Five of the ten values can be negative, and the training loss is
    nn.BCEWithLogitsLoss, which cannot represent a target below zero: a negative
    target drives the logit towards -inf and the field collapses to 0, which
    inference then reads as "full left" rather than "no movement". Recording
    therefore stores signed fields mapped through ``(v + 1) / 2``.
    """

    def test_block_has_ten_sequentially_indexed_slots(self):
        from bot_mmorpg.config.action_mapping import MOUSE_FIELDS, MOUSE_OUTPUT_SIZE

        assert MOUSE_OUTPUT_SIZE == 10
        assert len(MOUSE_FIELDS) == MOUSE_OUTPUT_SIZE
        assert [f.index for f in MOUSE_FIELDS] == list(range(MOUSE_OUTPUT_SIZE))

    def test_slot_order_matches_the_recorder(self):
        """collect_data appends mouse_state.to_array() verbatim, so the field
        table and the serializer have to agree slot for slot. Each slot gets a
        distinct value, so a reordering in either place cannot pass by luck."""
        from dataclasses import replace

        from bot_mmorpg.config.action_mapping import MOUSE_FIELDS
        from bot_mmorpg.scripts.mouse_capture import MouseState

        state = replace(
            MouseState(),
            **{field.name: i / 10.0 for i, field in enumerate(MOUSE_FIELDS)},
        )
        assert list(state.to_array()) == pytest.approx([i / 10.0 for i in range(10)])

    def test_signed_fields_are_exactly_the_ones_that_go_negative(self):
        from bot_mmorpg.config.action_mapping import (
            MOUSE_FIELDS,
            MOUSE_SIGNED_FIELD_COUNT,
        )

        signed = {f.name for f in MOUSE_FIELDS if f.signed}
        assert signed == {"dx", "dy", "vx", "vy", "scroll"}
        assert MOUSE_SIGNED_FIELD_COUNT == len(signed) == 5

    def test_normalization_puts_every_field_in_range(self):
        """BCE cannot represent a negative target, so this is the property
        that makes the mouse block trainable at all."""
        from bot_mmorpg.config.action_mapping import (
            MOUSE_FIELDS,
            normalize_mouse_vector,
        )

        raw = [-1.0 if f.signed else 0.5 for f in MOUSE_FIELDS]
        out = normalize_mouse_vector(raw)
        assert len(out) == len(MOUSE_FIELDS)
        assert all(0.0 <= v <= 1.0 for v in out)

    def test_normalization_is_lossless_for_a_real_snapshot(self):
        """(v + 1) / 2 then (p - 0.5) * 2 has to give the captured value back,
        or the bot moves the camera by a different amount than the recording."""
        from bot_mmorpg.config.action_mapping import (
            MOUSE_FIELDS,
            denormalize_mouse_value,
            mouse_field,
            normalize_mouse_vector,
        )
        from bot_mmorpg.scripts.mouse_capture import MouseState

        state = MouseState(
            x=0.13,
            y=0.87,
            dx=-0.4,
            dy=0.9,
            vx=0.0,
            vy=-1.0,
            lmb=1,
            rmb=0,
            mmb=1,
            scroll=-0.25,
        )
        raw = list(state.to_array())
        normalized = normalize_mouse_vector(raw)
        restored = [
            denormalize_mouse_value(mouse_field(field.name), value)
            for field, value in zip(MOUSE_FIELDS, normalized)
        ]
        assert restored == pytest.approx(raw, abs=1e-6)

    def test_neutral_input_becomes_the_neutral_target(self):
        """A field captured as 0 has to record 0.5, not 0.0. Inference maps 0.5
        back to 0 and leaves the camera alone; it would read 0.0 as full left."""
        from bot_mmorpg.config.action_mapping import (
            denormalize_mouse_value,
            mouse_field,
            normalize_mouse_vector,
        )

        out = normalize_mouse_vector([0.0] * 10)
        assert out[mouse_field("dx").index] == 0.5
        assert denormalize_mouse_value(mouse_field("dx"), 0.5) == 0.0

    def test_wrong_length_is_rejected(self):
        from bot_mmorpg.config.action_mapping import normalize_mouse_vector

        with pytest.raises(ValueError, match="mouse values"):
            normalize_mouse_vector([0.0] * 6)

    def test_scrollable_fields_stay_in_range_after_capture(self):
        """scroll_accum is unbounded, so snapshot() has to clamp it; an
        unclamped value would normalise past 1.0 and become unreachable."""
        from bot_mmorpg.config.action_mapping import (
            mouse_field,
            normalize_mouse_vector,
        )
        from bot_mmorpg.scripts import mouse_capture

        mc = mouse_capture.MouseCapture()
        scroll_idx = mouse_field("scroll").index

        for accum, expected in ((50.0, 1.0), (-50.0, 0.0)):
            with mc._state.lock:
                mc._state.scroll_accum = accum
            out = normalize_mouse_vector(mc.snapshot().to_array())
            assert all(0.0 <= v <= 1.0 for v in out)
            assert out[scroll_idx] == pytest.approx(expected)


class TestMouseBlockReachesTheBot:
    """Inference has to read the block the recorder wrote."""

    def test_field_table_is_available_to_the_bot(self):
        from bot_mmorpg.scripts import test_model

        assert test_model.MOUSE_OUTPUT_SIZE == 10
        assert {f.name for f in test_model.MOUSE_FIELDS} == {
            "x",
            "y",
            "dx",
            "dy",
            "vx",
            "vy",
            "lmb",
            "rmb",
            "mmb",
            "scroll",
        }

    def test_bot_reads_slots_by_name_not_by_index(self):
        """A hardcoded 2/3/6/9 in the current-format branch would silently
        read the wrong slot the day MOUSE_FIELDS is reordered. The legacy
        branch may keep literal indices: that 6-value order is frozen by the
        checkpoints already written to disk, so a literal is the honest
        encoding there.
        """
        import inspect
        import re

        from bot_mmorpg.scripts import test_model

        source = inspect.getsource(test_model.InferenceEngine.execute_mouse)
        current, marker, legacy = source.partition(
            "elif len(mouse_preds) >= _LEGACY_MOUSE_OUTPUT_SIZE:"
        )
        assert marker, "legacy branch marker not found in execute_mouse"

        # Current format: every slot is resolved through the field table.
        assert "_MOUSE_FIELD[" in current
        assert not re.search(r"mouse_preds\[\d+\]", current)

        # Legacy format: fixed [x, y, lmb, rmb, mmb, scroll] order.
        assert sorted(re.findall(r"mouse_preds\[(\d+)\]", legacy)) == ["2", "3", "5"]

    def test_legacy_width_does_not_steer_the_camera(self):
        """A 6-value checkpoint has no delta, so dx must denormalise to 0.
        Mapping a placeholder 0.0 would read as full left every frame."""
        from bot_mmorpg.config.action_mapping import (
            denormalize_mouse_value,
            mouse_field,
        )

        assert denormalize_mouse_value(mouse_field("dx"), 0.5) == 0.0
        assert denormalize_mouse_value(mouse_field("dy"), 0.5) == 0.0


class TestModelHubAcceptsBothWidths:
    """The catalog tool validates a model against a game blueprint; a model
    recorded with --mouse is wider than the blueprint declares."""

    @pytest.mark.parametrize("classes", [29, 39])
    def test_matching_width_is_accepted(self, classes):
        from modelhub.validator import validate_compatibility

        blueprint = {
            "id": "genshin_impact",
            "expected_input_shape": [480, 270, 3],
            "expected_classes": 29,
        }
        profile = {
            "profile_name": "m",
            "architecture": "efficientnet_lstm",
            "input_shape": [480, 270, 3],
            "classes": classes,
        }
        assert validate_compatibility(blueprint, profile)[0] is True

    @pytest.mark.parametrize("classes", [28, 35, 40])
    def test_other_widths_are_rejected(self, classes):
        from modelhub.validator import validate_compatibility

        blueprint = {
            "id": "genshin_impact",
            "expected_input_shape": [480, 270, 3],
            "expected_classes": 29,
        }
        profile = {
            "profile_name": "m",
            "architecture": "efficientnet_lstm",
            "input_shape": [480, 270, 3],
            "classes": classes,
        }
        ok, message = validate_compatibility(blueprint, profile)
        assert ok is False
        assert "Class count mismatch" in message

    def test_modelhub_widths_match_the_pipeline(self):
        from modelhub.action_space import (
            ACCEPTED_CLASS_COUNTS,
            BASE_ACTION_COUNT,
            MOUSE_OUTPUT_SIZE,
        )
        from bot_mmorpg.config.action_mapping import MOUSE_OUTPUT_SIZE as RECORDED
        from bot_mmorpg.scripts import collect_data

        assert MOUSE_OUTPUT_SIZE == RECORDED
        assert BASE_ACTION_COUNT == collect_data.base_action_count()
        assert ACCEPTED_CLASS_COUNTS == (29, 39)


# =============================================================================
# Game profiles
# =============================================================================


class TestGameProfilesAreWired:
    """A profile that disagrees with the pipeline would poison a dataset."""

    def test_every_shipped_profile_matches_the_pipeline(self):
        from bot_mmorpg.config.action_mapping import ACTION_SPACE_STANDARD
        from bot_mmorpg.config.profile_loader import GameProfileLoader
        from bot_mmorpg.scripts import collect_data

        loader = GameProfileLoader()
        game_ids = [g["id"] for g in loader.list_games()]
        assert game_ids, "no game profiles found"

        for game_id in game_ids:
            profile = loader.load(game_id)
            collect_data.validate_profile(profile)
            assert profile.action_space == ACTION_SPACE_STANDARD.name, game_id
            assert profile.num_actions == 29, game_id
            assert list(profile.recommended_input_size) == [480, 270], game_id
            for tier, cfg in profile.hardware_tiers.items():
                assert list(cfg.input_size) == [480, 270], f"{game_id}/{tier}"

    def test_template_profile_also_matches(self):
        from bot_mmorpg.config.profile_loader import GameProfileLoader
        from bot_mmorpg.scripts import collect_data

        loader = GameProfileLoader()
        text = loader.get_template_path().read_text(encoding="utf-8")
        assert 'action_space: "standard"' in text
        assert "num_actions: 29" in text
        assert "recommended_input_size: [480, 270]" in text

        # And it parses.
        collect_data.validate_profile(loader.load("_template"))


class TestProfileValidation:
    """validate_profile rejects profiles the pipeline cannot honour."""

    @staticmethod
    def _profile(**fields):
        base = {
            "id": "test_game",
            "action_space": "standard",
            "num_actions": 29,
            "recommended_input_size": [480, 270],
        }
        base.update(fields)
        return type("FakeProfile", (), base)()

    def test_none_passes(self):
        from bot_mmorpg.scripts import collect_data

        collect_data.validate_profile(None)

    def test_base_count_passes(self):
        from bot_mmorpg.scripts import collect_data

        collect_data.validate_profile(self._profile(num_actions=29))

    def test_count_including_mouse_passes(self):
        from bot_mmorpg.scripts import collect_data

        collect_data.validate_profile(self._profile(num_actions=39))

    @pytest.mark.parametrize("declared", [0, 12, 16, 28, 30, 35, 36, 38, 40, 48, -1])
    def test_other_counts_are_rejected(self, declared):
        from bot_mmorpg.scripts import collect_data

        with pytest.raises(collect_data.DataCollectionError):
            collect_data.validate_profile(self._profile(num_actions=declared))

    def test_mismatched_space_only_warns(self):
        """action_space is descriptive; num_actions is the hard contract."""
        from bot_mmorpg.scripts import collect_data

        collect_data.validate_profile(self._profile(action_space="discrete"))

    def test_unreadable_count_is_rejected(self):
        from bot_mmorpg.scripts import collect_data

        with pytest.raises(collect_data.DataCollectionError):
            collect_data.validate_profile(self._profile(num_actions="lots"))


class TestTargetSizeResolution:
    """The profile may ask for a size; the pipeline has the final say."""

    @staticmethod
    def _profile(size):
        return type(
            "FakeProfile",
            (),
            {"id": "test_game", "recommended_input_size": size},
        )()

    def test_no_profile_uses_the_pipeline_size(self):
        from bot_mmorpg.scripts import collect_data

        assert collect_data.resolve_target_size(None) == (480, 270)

    def test_matching_size_is_honoured(self):
        from bot_mmorpg.scripts import collect_data

        assert collect_data.resolve_target_size(self._profile([480, 270])) == (480, 270)

    @pytest.mark.parametrize(
        "size",
        [[224, 224], [256, 256], [160, 160], [1920, 1080], "abc", [], [0, 0], None],
    )
    def test_other_sizes_fall_back_to_the_pipeline(self, size):
        from bot_mmorpg.scripts import collect_data

        assert collect_data.resolve_target_size(self._profile(size)) == (480, 270)


# =============================================================================
# Inference (needs torch)
# =============================================================================


class TestInferenceMatchesTheActionSpace:
    """test_model.py must drive exactly the slots the action space defines."""

    def test_action_names_unchanged(self):
        from bot_mmorpg.scripts.test_model import ACTION_NAMES

        assert ACTION_NAMES == LEGACY_ACTION_NAMES

    def test_action_weights_unchanged(self):
        from bot_mmorpg.scripts.test_model import ACTION_WEIGHTS

        assert ACTION_WEIGHTS.shape == (29,)
        assert ACTION_WEIGHTS[0] == 2.5
        assert ACTION_WEIGHTS[8] > 0  # nokeys still gets a weight

    def test_keyboard_handlers_cover_slots_0_to_8(self):
        from bot_mmorpg.scripts.test_model import KEYBOARD_ACTIONS

        assert sorted(KEYBOARD_ACTIONS) == list(range(9))

    def test_keyboard_slot_8_is_nokeys(self):
        from bot_mmorpg.scripts.test_model import ACTION_NAMES, KEYBOARD_ACTIONS

        slot = 8
        assert ACTION_NAMES[slot] == "nokeys"
        assert callable(KEYBOARD_ACTIONS[slot])
        # The handler must not press anything.
        assert KEYBOARD_ACTIONS[slot]() is None

    def test_gamepad_slots_are_the_same_ten_as_before(self):
        from bot_mmorpg.scripts.test_model import GAMEPAD_ACTIONS

        assert sorted(GAMEPAD_ACTIONS) == [9, 10, 11, 12, 13, 14, 25, 26, 27, 28]

    def test_unmapped_gamepad_slots_are_reported_not_swallowed(self):
        from bot_mmorpg.scripts.test_model import UNIMPLEMENTED_GAMEPAD_ACTIONS

        assert [slot for slot, _ in UNIMPLEMENTED_GAMEPAD_ACTIONS] == list(
            range(15, 25)
        )

    def test_build_action_weights_shapes(self):
        from bot_mmorpg.scripts.test_model import build_action_weights

        assert build_action_weights(29).shape == (29,)
        assert build_action_weights(35).shape == (35,)
        assert build_action_weights(39).shape == (39,)

    def test_base_weight_table_matches_the_action_space(self):
        """test_model.py raises at import if these drift apart, so a change
        here is a change to how every trained loss is weighted."""
        from bot_mmorpg.scripts import test_model

        assert len(test_model._BASE_ACTION_WEIGHTS) == test_model._BASE_ACTION_COUNT
        assert test_model._BASE_ACTION_COUNT == 29

    def test_ten_value_mouse_block_matches_the_collector(self):
        """The weights have to describe the same ten slots the recorder writes,
        in the same order, or a trained loss is weighted on the wrong output."""
        from bot_mmorpg.config.action_mapping import MOUSE_FIELDS
        from bot_mmorpg.scripts import test_model

        assert len(test_model._MOUSE_WEIGHTS_10) == len(MOUSE_FIELDS)

        weights = test_model.build_action_weights(39)
        assert weights.shape == (39,)
        # Continuous outputs (position/delta/velocity) must not out-vote the
        # discrete actions; buttons must.
        for field in MOUSE_FIELDS:
            if field.name in ("lmb", "rmb", "mmb"):
                assert weights[29 + field.index] >= 0.8, field.name
            elif field.name != "scroll":
                assert weights[29 + field.index] < 0.5, field.name

    def test_legacy_six_value_mouse_block_still_loads(self):
        """Checkpoints recorded before the block grew to ten values are still
        29 + 6 wide, and must keep their original weight layout."""
        from bot_mmorpg.scripts import test_model

        assert len(test_model._MOUSE_WEIGHTS_6) == 6
        weights = test_model.build_action_weights(35)
        assert weights.shape == (35,)
        assert weights[29] < 0.5  # x
        assert weights[30] < 0.5  # y
        assert weights[31] >= 0.8  # lmb
