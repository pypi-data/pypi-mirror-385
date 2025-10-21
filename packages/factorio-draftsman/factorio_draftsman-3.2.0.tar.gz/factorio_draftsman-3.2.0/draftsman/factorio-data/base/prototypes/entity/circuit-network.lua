require("prototypes.entity.combinator-pictures")
local hit_effects = require("prototypes.entity.hit-effects")
local sounds = require("prototypes.entity.sounds")
local simulations = require("__base__.prototypes.factoriopedia-simulations")

data:extend
{
  generate_arithmetic_combinator
  {
    type = "arithmetic-combinator",
    name = "arithmetic-combinator",
    icon = "__base__/graphics/icons/arithmetic-combinator.png",
    flags = {"placeable-neutral", "player-creation"},
    minable = {mining_time = 0.1, result = "arithmetic-combinator"},
    fast_replaceable_group = "arithmetic-combinator",
    max_health = 150,
    corpse = "arithmetic-combinator-remnants",
    dying_explosion = "arithmetic-combinator-explosion",
    collision_box = {{-0.35, -0.65}, {0.35, 0.65}},
    selection_box = {{-0.5, -1}, {0.5, 1}},
    damaged_trigger_effect = hit_effects.entity(),
    icon_draw_specification = {scale = 0.5},

    energy_source =
    {
      type = "electric",
      usage_priority = "secondary-input"
    },
    active_energy_usage = "1kW",

    working_sound =
    {
      sound = {filename = "__base__/sound/combinator.ogg", volume = 0.45, audible_distance_modifier = 0.2},
      fade_in_ticks = 4,
      fade_out_ticks = 20,
      match_speed_to_activity = true
    },
    open_sound = sounds.combinator_open,
    close_sound = sounds.combinator_close,

    activity_led_light =
    {
      intensity = 0,
      size = 1,
      color = {r = 1.0, g = 1.0, b = 1.0}
    },

    activity_led_light_offsets =
    {
      {0.234375, -0.484375},
      {0.5, 0},
      {-0.265625, 0.140625},
      {-0.453125, -0.359375}
    },

    screen_light =
    {
      intensity = 0,
      size = 0.6,
      color = {r = 1.0, g = 1.0, b = 1.0}
    },

    screen_light_offsets =
    {
      {0.015625, -0.234375},
      {0.015625, -0.296875},
      {0.015625, -0.234375},
      {0.015625, -0.296875}
    },

    input_connection_bounding_box = {{-0.5, 0}, {0.5, 1}},
    output_connection_bounding_box = {{-0.5, -1}, {0.5, 0}},

    circuit_wire_max_distance = combinator_circuit_wire_max_distance
  },

  generate_decider_combinator
  {
    type = "decider-combinator",
    name = "decider-combinator",
    icon = "__base__/graphics/icons/decider-combinator.png",
    flags = {"placeable-neutral", "player-creation"},
    minable = {mining_time = 0.1, result = "decider-combinator"},
    fast_replaceable_group = "decider-combinator",
    max_health = 150,
    corpse = "decider-combinator-remnants",
    dying_explosion = "decider-combinator-explosion",
    collision_box = {{-0.35, -0.65}, {0.35, 0.65}},
    selection_box = {{-0.5, -1}, {0.5, 1}},
    damaged_trigger_effect = hit_effects.entity(),
    icon_draw_specification = {scale = 0.5},

    energy_source =
    {
      type = "electric",
      usage_priority = "secondary-input"
    },
    active_energy_usage = "1kW",

    working_sound =
    {
      sound = {filename = "__base__/sound/combinator.ogg", volume = 0.45, audible_distance_modifier = 0.2},
      fade_in_ticks = 4,
      fade_out_ticks = 20,
      match_speed_to_activity = true
    },
    open_sound = sounds.combinator_open,
    close_sound = sounds.combinator_close,

    activity_led_light =
    {
      intensity = 0,
      size = 1,
      color = {r = 1.0, g = 1.0, b = 1.0}
    },

    activity_led_light_offsets =
    {
      {0.265625, -0.53125},
      {0.515625, -0.078125},
      {-0.25, 0.03125},
      {-0.46875, -0.5}
    },

    screen_light =
    {
      intensity = 0,
      size = 0.6,
      color = {r = 1.0, g = 1.0, b = 1.0}
    },

    screen_light_offsets =
    {
      {0.015625, -0.265625},
      {0.015625, -0.359375},
      {0.015625, -0.265625},
      {0.015625, -0.359375}
    },

    input_connection_bounding_box = {{-0.5, 0}, {0.5, 1}},
    output_connection_bounding_box = {{-0.5, -1}, {0.5, 0}},

    circuit_wire_max_distance = combinator_circuit_wire_max_distance
  },

  generate_constant_combinator
  {
    type = "constant-combinator",
    name = "constant-combinator",
    icon = "__base__/graphics/icons/constant-combinator.png",
    flags = {"placeable-neutral", "player-creation"},
    minable = {mining_time = 0.1, result = "constant-combinator"},
    max_health = 120,
    corpse = "constant-combinator-remnants",
    dying_explosion = "constant-combinator-explosion",
    collision_box = {{-0.35, -0.35}, {0.35, 0.35}},
    selection_box = {{-0.5, -0.5}, {0.5, 0.5}},
    damaged_trigger_effect = hit_effects.entity(),
    fast_replaceable_group = "constant-combinator",
    open_sound = sounds.combinator_open,
    close_sound = sounds.combinator_close,
    icon_draw_specification = {scale = 0.7},
    activity_led_light =
    {
      intensity = 0,
      size = 1,
      color = {r = 1.0, g = 1.0, b = 1.0}
    },

    activity_led_light_offsets =
    {
      {0.296875, -0.40625},
      {0.25, -0.03125},
      {-0.296875, -0.078125},
      {-0.21875, -0.46875}
    },

    circuit_wire_max_distance = combinator_circuit_wire_max_distance
  },

  {
    type = "programmable-speaker",
    name = "programmable-speaker",
    icon = "__base__/graphics/icons/programmable-speaker.png",
    flags = {"placeable-neutral", "player-creation"},
    minable = {mining_time = 0.1, result = "programmable-speaker"},
    fast_replaceable_group = "programmable-speaker",
    max_health = 150,
    corpse = "programmable-speaker-remnants",
    dying_explosion = "programmable-speaker-explosion",
    collision_box = {{-0.3, -0.3}, {0.3, 0.3}},
    selection_box = {{-0.5, -0.5}, {0.5, 0.5}},
    damaged_trigger_effect = hit_effects.entity({{-0.2, -2},{0.2, 0.2}}),
    drawing_box_vertical_extension = 2,
    open_sound = sounds.machine_open,
    close_sound = sounds.machine_close,
    energy_source =
    {
      type = "electric",
      usage_priority = "secondary-input"
    },
    energy_usage_per_tick = "2kW",

    sprite =
    {
      layers =
      {
        {
          filename = "__base__/graphics/entity/programmable-speaker/programmable-speaker.png",
          priority = "extra-high",
          width = 59,
          height = 178,
          shift = util.by_pixel(-2.25, -39.5),
          scale = 0.5
        },
        {
          filename = "__base__/graphics/entity/programmable-speaker/programmable-speaker-shadow.png",
          priority = "extra-high",
          width = 237,
          height = 50,
          shift = util.by_pixel(52.75, -3),
          draw_as_shadow = true,
          scale = 0.5
        }
      }
    },

    audible_distance_modifier = 2, --multiplies the default 40 tiles of audible distance by this number
    maximum_polyphony = 10, --maximum number of samples that can play at the same time

    instruments =
    {
      {
        name = "alarms",
        notes =
        {
         { name="alarm-1",  sound = { filename = "__base__/sound/programmable-speaker/alarm-1.ogg", modifiers = volume_multiplier("main-menu", 0.8)}},
         { name="alarm-2",  sound = { filename = "__base__/sound/programmable-speaker/alarm-2.ogg" }},
         { name="buzzer-1",  sound = { filename = "__base__/sound/programmable-speaker/buzzer-1.ogg" }},
         { name="buzzer-2",  sound = { filename = "__base__/sound/programmable-speaker/buzzer-2.ogg" }},
         { name="buzzer-3",  sound = { filename = "__base__/sound/programmable-speaker/buzzer-3.ogg" }},
         { name="ring",  sound = { filename = "__base__/sound/programmable-speaker/ring.ogg", preload = false }},
         { name="siren",  sound = { filename = "__base__/sound/programmable-speaker/siren.ogg", preload = false }}
        }
      },
      {
        name = "miscellaneous",
        notes =
        {
          { name = "achievement-unlocked",  sound = { filename = "__core__/sound/achievement-unlocked.ogg" }},
          { name = "alert-destroyed",  sound = { filename = "__core__/sound/alert-destroyed.ogg" }},
          { name = "armor-insert",  sound = { filename = "__core__/sound/armor-insert.ogg" }},
          { name = "armor-remove",  sound = { filename = "__core__/sound/armor-remove.ogg" }},
          { name = "cannot-build",  sound = { filename = "__core__/sound/cannot-build.ogg" }},
          { name = "console-message",  sound = { filename = "__core__/sound/console-message.ogg" }},
          { name = "crafting-finished",  sound = { filename = "__core__/sound/crafting-finished.ogg" }},
          { name = "game-lost",  sound = { filename = "__core__/sound/game-lost.ogg" }},
          { name = "game-won",  sound = { filename = "__core__/sound/game-won.ogg" }},
          { name = "gui-click",  sound = { filename = "__core__/sound/gui-click.ogg" }},
          { name = "gui-click-2",  sound = { filename = "__core__/sound/list-box-click.ogg" }},
          { name = "inventory-move",  sound = { filename = "__core__/sound/inventory-move.ogg" }},
          { name = "new-objective",  sound = { filename = "__core__/sound/new-objective.ogg" }},
          { name = "research-completed",  sound = { filename = "__core__/sound/research-completed.ogg" }},
          { name = "scenario-message",  sound = { filename = "__core__/sound/scenario-message.ogg" }}
        }
      },
      {
        name = "drum-kit",
        notes =
        {
          { name = "kick-1",  sound = { filename = "__base__/sound/programmable-speaker/kit-01.ogg" }},
          { name = "kick-2",  sound = { filename = "__base__/sound/programmable-speaker/kit-02.ogg" }},
          { name = "snare-1", sound = { filename = "__base__/sound/programmable-speaker/kit-03.ogg" }},
          { name = "snare-2", sound = { filename = "__base__/sound/programmable-speaker/kit-04.ogg" }},
          { name = "snare-3", sound = { filename = "__base__/sound/programmable-speaker/kit-05.ogg" }},
          { name = "hat-1",   sound = { filename = "__base__/sound/programmable-speaker/kit-06.ogg" }},
          { name = "hat-2",   sound = { filename = "__base__/sound/programmable-speaker/kit-07.ogg" }},
          { name = "fx",  sound = { filename = "__base__/sound/programmable-speaker/kit-08.ogg" }},
          { name = "high-q",  sound = { filename = "__base__/sound/programmable-speaker/kit-09.ogg" }},
          { name = "perc-1",  sound = { filename = "__base__/sound/programmable-speaker/kit-10.ogg" }},
          { name = "perc-2",  sound = { filename = "__base__/sound/programmable-speaker/kit-11.ogg" }},
          { name = "crash",  sound = { filename = "__base__/sound/programmable-speaker/kit-12.ogg" }},
          { name = "reverse-cymbal",  sound = { filename = "__base__/sound/programmable-speaker/kit-13.ogg" }},
          { name = "clap",  sound = { filename = "__base__/sound/programmable-speaker/kit-14.ogg" }},
          { name = "shaker",  sound = { filename = "__base__/sound/programmable-speaker/kit-15.ogg" }},
          { name = "cowbell",  sound = { filename = "__base__/sound/programmable-speaker/kit-16.ogg" }},
          { name = "triangle",  sound = { filename = "__base__/sound/programmable-speaker/kit-17.ogg" }}
        }
      },
      {
        name = "piano",
        notes =
        {
          { name = "F3",  sound = { filename = "__base__/sound/programmable-speaker/piano1-01.ogg" }},
          { name = "F#3", sound = { filename = "__base__/sound/programmable-speaker/piano1-02.ogg" }},
          { name = "G3",  sound = { filename = "__base__/sound/programmable-speaker/piano1-03.ogg" }},
          { name = "G#3", sound = { filename = "__base__/sound/programmable-speaker/piano1-04.ogg" }},
          { name = "A3",  sound = { filename = "__base__/sound/programmable-speaker/piano1-05.ogg" }},
          { name = "A#3", sound = { filename = "__base__/sound/programmable-speaker/piano1-06.ogg" }},
          { name = "B3",  sound = { filename = "__base__/sound/programmable-speaker/piano1-07.ogg" }},
          { name = "C4",  sound = { filename = "__base__/sound/programmable-speaker/piano1-08.ogg" }},
          { name = "C#4", sound = { filename = "__base__/sound/programmable-speaker/piano1-09.ogg" }},
          { name = "D4",  sound = { filename = "__base__/sound/programmable-speaker/piano1-10.ogg" }},
          { name = "D#4", sound = { filename = "__base__/sound/programmable-speaker/piano1-11.ogg" }},
          { name = "E4",  sound = { filename = "__base__/sound/programmable-speaker/piano1-12.ogg" }},
          { name = "F4",  sound = { filename = "__base__/sound/programmable-speaker/piano1-13.ogg" }},
          { name = "F#4", sound = { filename = "__base__/sound/programmable-speaker/piano1-14.ogg" }},
          { name = "G4",  sound = { filename = "__base__/sound/programmable-speaker/piano1-15.ogg" }},
          { name = "G#4", sound = { filename = "__base__/sound/programmable-speaker/piano1-16.ogg" }},
          { name = "A4",  sound = { filename = "__base__/sound/programmable-speaker/piano1-17.ogg" }},
          { name = "A#4", sound = { filename = "__base__/sound/programmable-speaker/piano1-18.ogg" }},
          { name = "B4",  sound = { filename = "__base__/sound/programmable-speaker/piano1-19.ogg" }},
          { name = "C5",  sound = { filename = "__base__/sound/programmable-speaker/piano1-20.ogg" }},
          { name = "C#5", sound = { filename = "__base__/sound/programmable-speaker/piano1-21.ogg" }},
          { name = "D5",  sound = { filename = "__base__/sound/programmable-speaker/piano1-22.ogg" }},
          { name = "D#5", sound = { filename = "__base__/sound/programmable-speaker/piano1-23.ogg" }},
          { name = "E5",  sound = { filename = "__base__/sound/programmable-speaker/piano1-24.ogg" }},
          { name = "F5",  sound = { filename = "__base__/sound/programmable-speaker/piano1-25.ogg" }},
          { name = "F#5", sound = { filename = "__base__/sound/programmable-speaker/piano1-26.ogg" }},
          { name = "G5",  sound = { filename = "__base__/sound/programmable-speaker/piano1-27.ogg" }},
          { name = "G#5", sound = { filename = "__base__/sound/programmable-speaker/piano1-28.ogg" }},
          { name = "A5",  sound = { filename = "__base__/sound/programmable-speaker/piano1-29.ogg" }},
          { name = "A#5", sound = { filename = "__base__/sound/programmable-speaker/piano1-30.ogg" }},
          { name = "B5",  sound = { filename = "__base__/sound/programmable-speaker/piano1-31.ogg" }},
          { name = "C6",  sound = { filename = "__base__/sound/programmable-speaker/piano1-32.ogg" }},
          { name = "C#6", sound = { filename = "__base__/sound/programmable-speaker/piano1-33.ogg" }},
          { name = "D6",  sound = { filename = "__base__/sound/programmable-speaker/piano1-34.ogg" }},
          { name = "D#6", sound = { filename = "__base__/sound/programmable-speaker/piano1-35.ogg" }},
          { name = "E6",  sound = { filename = "__base__/sound/programmable-speaker/piano1-36.ogg" }},
          { name = "F6",  sound = { filename = "__base__/sound/programmable-speaker/piano1-37.ogg" }},
          { name = "F#6", sound = { filename = "__base__/sound/programmable-speaker/piano1-38.ogg" }},
          { name = "G6",  sound = { filename = "__base__/sound/programmable-speaker/piano1-39.ogg" }},
          { name = "G#6", sound = { filename = "__base__/sound/programmable-speaker/piano1-40.ogg" }},
          { name = "A6",  sound = { filename = "__base__/sound/programmable-speaker/piano1-41.ogg" }},
          { name = "A#6", sound = { filename = "__base__/sound/programmable-speaker/piano1-42.ogg" }},
          { name = "B6",  sound = { filename = "__base__/sound/programmable-speaker/piano1-43.ogg" }},
          { name = "C7",  sound = { filename = "__base__/sound/programmable-speaker/piano1-44.ogg" }},
          { name = "C#7", sound = { filename = "__base__/sound/programmable-speaker/piano1-45.ogg" }},
          { name = "D7",  sound = { filename = "__base__/sound/programmable-speaker/piano1-46.ogg" }},
          { name = "D#7", sound = { filename = "__base__/sound/programmable-speaker/piano1-47.ogg" }},
          { name = "E7",  sound = { filename = "__base__/sound/programmable-speaker/piano1-48.ogg" }}
        }
      },
      {
        name = "bass",
        notes =
        {
          { name = "F2",  sound = { filename = "__base__/sound/programmable-speaker/bass-01.ogg" }},
          { name = "F#2", sound = { filename = "__base__/sound/programmable-speaker/bass-02.ogg" }},
          { name = "G2",  sound = { filename = "__base__/sound/programmable-speaker/bass-03.ogg" }},
          { name = "G#2", sound = { filename = "__base__/sound/programmable-speaker/bass-04.ogg" }},
          { name = "A2",  sound = { filename = "__base__/sound/programmable-speaker/bass-05.ogg" }},
          { name = "A#2", sound = { filename = "__base__/sound/programmable-speaker/bass-06.ogg" }},
          { name = "B2",  sound = { filename = "__base__/sound/programmable-speaker/bass-07.ogg" }},
          { name = "C3",  sound = { filename = "__base__/sound/programmable-speaker/bass-08.ogg" }},
          { name = "C#3", sound = { filename = "__base__/sound/programmable-speaker/bass-09.ogg" }},
          { name = "D3",  sound = { filename = "__base__/sound/programmable-speaker/bass-10.ogg" }},
          { name = "D#3", sound = { filename = "__base__/sound/programmable-speaker/bass-11.ogg" }},
          { name = "E3",  sound = { filename = "__base__/sound/programmable-speaker/bass-12.ogg" }},
          { name = "F3",  sound = { filename = "__base__/sound/programmable-speaker/bass-13.ogg" }},
          { name = "F#3", sound = { filename = "__base__/sound/programmable-speaker/bass-14.ogg" }},
          { name = "G3",  sound = { filename = "__base__/sound/programmable-speaker/bass-15.ogg" }},
          { name = "G#3", sound = { filename = "__base__/sound/programmable-speaker/bass-16.ogg" }},
          { name = "A3",  sound = { filename = "__base__/sound/programmable-speaker/bass-17.ogg" }},
          { name = "A#3", sound = { filename = "__base__/sound/programmable-speaker/bass-18.ogg" }},
          { name = "B3",  sound = { filename = "__base__/sound/programmable-speaker/bass-19.ogg" }},
          { name = "C4",  sound = { filename = "__base__/sound/programmable-speaker/bass-20.ogg" }},
          { name = "C#4", sound = { filename = "__base__/sound/programmable-speaker/bass-21.ogg" }},
          { name = "D4",  sound = { filename = "__base__/sound/programmable-speaker/bass-22.ogg" }},
          { name = "D#4", sound = { filename = "__base__/sound/programmable-speaker/bass-23.ogg" }},
          { name = "E4",  sound = { filename = "__base__/sound/programmable-speaker/bass-24.ogg" }},
          { name = "F4",  sound = { filename = "__base__/sound/programmable-speaker/bass-25.ogg" }},
          { name = "F#4", sound = { filename = "__base__/sound/programmable-speaker/bass-26.ogg" }},
          { name = "G4",  sound = { filename = "__base__/sound/programmable-speaker/bass-27.ogg" }},
          { name = "G#4", sound = { filename = "__base__/sound/programmable-speaker/bass-28.ogg" }},
          { name = "A4",  sound = { filename = "__base__/sound/programmable-speaker/bass-29.ogg" }},
          { name = "A#4", sound = { filename = "__base__/sound/programmable-speaker/bass-30.ogg" }},
          { name = "B4",  sound = { filename = "__base__/sound/programmable-speaker/bass-31.ogg" }},
          { name = "C5",  sound = { filename = "__base__/sound/programmable-speaker/bass-32.ogg" }},
          { name = "C#5", sound = { filename = "__base__/sound/programmable-speaker/bass-33.ogg" }},
          { name = "D5",  sound = { filename = "__base__/sound/programmable-speaker/bass-34.ogg" }},
          { name = "D#5", sound = { filename = "__base__/sound/programmable-speaker/bass-35.ogg" }},
          { name = "E5",  sound = { filename = "__base__/sound/programmable-speaker/bass-36.ogg" }}
        }
      },
      {
        name = "lead",
        notes =
        {
          { name = "F2",  sound = { filename = "__base__/sound/programmable-speaker/lead-01.ogg" }},
          { name = "F#2", sound = { filename = "__base__/sound/programmable-speaker/lead-02.ogg" }},
          { name = "G2",  sound = { filename = "__base__/sound/programmable-speaker/lead-03.ogg" }},
          { name = "G#2", sound = { filename = "__base__/sound/programmable-speaker/lead-04.ogg" }},
          { name = "A2",  sound = { filename = "__base__/sound/programmable-speaker/lead-05.ogg" }},
          { name = "A#2", sound = { filename = "__base__/sound/programmable-speaker/lead-06.ogg" }},
          { name = "B2",  sound = { filename = "__base__/sound/programmable-speaker/lead-07.ogg" }},
          { name = "C3",  sound = { filename = "__base__/sound/programmable-speaker/lead-08.ogg" }},
          { name = "C#3", sound = { filename = "__base__/sound/programmable-speaker/lead-09.ogg" }},
          { name = "D3",  sound = { filename = "__base__/sound/programmable-speaker/lead-10.ogg" }},
          { name = "D#3", sound = { filename = "__base__/sound/programmable-speaker/lead-11.ogg" }},
          { name = "E3",  sound = { filename = "__base__/sound/programmable-speaker/lead-12.ogg" }},
          { name = "F3",  sound = { filename = "__base__/sound/programmable-speaker/lead-13.ogg" }},
          { name = "F#3", sound = { filename = "__base__/sound/programmable-speaker/lead-14.ogg" }},
          { name = "G3",  sound = { filename = "__base__/sound/programmable-speaker/lead-15.ogg" }},
          { name = "G#3", sound = { filename = "__base__/sound/programmable-speaker/lead-16.ogg" }},
          { name = "A3",  sound = { filename = "__base__/sound/programmable-speaker/lead-17.ogg" }},
          { name = "A#3", sound = { filename = "__base__/sound/programmable-speaker/lead-18.ogg" }},
          { name = "B3",  sound = { filename = "__base__/sound/programmable-speaker/lead-19.ogg" }},
          { name = "C4",  sound = { filename = "__base__/sound/programmable-speaker/lead-20.ogg" }},
          { name = "C#4", sound = { filename = "__base__/sound/programmable-speaker/lead-21.ogg" }},
          { name = "D4",  sound = { filename = "__base__/sound/programmable-speaker/lead-22.ogg" }},
          { name = "D#4", sound = { filename = "__base__/sound/programmable-speaker/lead-23.ogg" }},
          { name = "E4",  sound = { filename = "__base__/sound/programmable-speaker/lead-24.ogg" }},
          { name = "F4",  sound = { filename = "__base__/sound/programmable-speaker/lead-25.ogg" }},
          { name = "F#4", sound = { filename = "__base__/sound/programmable-speaker/lead-26.ogg" }},
          { name = "G4",  sound = { filename = "__base__/sound/programmable-speaker/lead-27.ogg" }},
          { name = "G#4", sound = { filename = "__base__/sound/programmable-speaker/lead-28.ogg" }},
          { name = "A4",  sound = { filename = "__base__/sound/programmable-speaker/lead-29.ogg" }},
          { name = "A#4", sound = { filename = "__base__/sound/programmable-speaker/lead-30.ogg" }},
          { name = "B4",  sound = { filename = "__base__/sound/programmable-speaker/lead-31.ogg" }},
          { name = "C5",  sound = { filename = "__base__/sound/programmable-speaker/lead-32.ogg" }},
          { name = "C#5", sound = { filename = "__base__/sound/programmable-speaker/lead-33.ogg" }},
          { name = "D5",  sound = { filename = "__base__/sound/programmable-speaker/lead-34.ogg" }},
          { name = "D#5", sound = { filename = "__base__/sound/programmable-speaker/lead-35.ogg" }},
          { name = "E5",  sound = { filename = "__base__/sound/programmable-speaker/lead-36.ogg" }}
        }
      },
      {
        name = "saw",
        notes =
        {
          { name = "F2",  sound = { filename = "__base__/sound/programmable-speaker/saw-01.ogg" }},
          { name = "F#2", sound = { filename = "__base__/sound/programmable-speaker/saw-02.ogg" }},
          { name = "G2",  sound = { filename = "__base__/sound/programmable-speaker/saw-03.ogg" }},
          { name = "G#2", sound = { filename = "__base__/sound/programmable-speaker/saw-04.ogg" }},
          { name = "A2",  sound = { filename = "__base__/sound/programmable-speaker/saw-05.ogg" }},
          { name = "A#2", sound = { filename = "__base__/sound/programmable-speaker/saw-06.ogg" }},
          { name = "B2",  sound = { filename = "__base__/sound/programmable-speaker/saw-07.ogg" }},
          { name = "C3",  sound = { filename = "__base__/sound/programmable-speaker/saw-08.ogg" }},
          { name = "C#3", sound = { filename = "__base__/sound/programmable-speaker/saw-09.ogg" }},
          { name = "D3",  sound = { filename = "__base__/sound/programmable-speaker/saw-10.ogg" }},
          { name = "D#3", sound = { filename = "__base__/sound/programmable-speaker/saw-11.ogg" }},
          { name = "E3",  sound = { filename = "__base__/sound/programmable-speaker/saw-12.ogg" }},
          { name = "F3",  sound = { filename = "__base__/sound/programmable-speaker/saw-13.ogg" }},
          { name = "F#3", sound = { filename = "__base__/sound/programmable-speaker/saw-14.ogg" }},
          { name = "G3",  sound = { filename = "__base__/sound/programmable-speaker/saw-15.ogg" }},
          { name = "G#3", sound = { filename = "__base__/sound/programmable-speaker/saw-16.ogg" }},
          { name = "A3",  sound = { filename = "__base__/sound/programmable-speaker/saw-17.ogg" }},
          { name = "A#3", sound = { filename = "__base__/sound/programmable-speaker/saw-18.ogg" }},
          { name = "B3",  sound = { filename = "__base__/sound/programmable-speaker/saw-19.ogg" }},
          { name = "C4",  sound = { filename = "__base__/sound/programmable-speaker/saw-20.ogg" }},
          { name = "C#4", sound = { filename = "__base__/sound/programmable-speaker/saw-21.ogg" }},
          { name = "D4",  sound = { filename = "__base__/sound/programmable-speaker/saw-22.ogg" }},
          { name = "D#4", sound = { filename = "__base__/sound/programmable-speaker/saw-23.ogg" }},
          { name = "E4",  sound = { filename = "__base__/sound/programmable-speaker/saw-24.ogg" }},
          { name = "F4",  sound = { filename = "__base__/sound/programmable-speaker/saw-25.ogg" }},
          { name = "F#4", sound = { filename = "__base__/sound/programmable-speaker/saw-26.ogg" }},
          { name = "G4",  sound = { filename = "__base__/sound/programmable-speaker/saw-27.ogg" }},
          { name = "G#4", sound = { filename = "__base__/sound/programmable-speaker/saw-28.ogg" }},
          { name = "A4",  sound = { filename = "__base__/sound/programmable-speaker/saw-29.ogg" }},
          { name = "A#4", sound = { filename = "__base__/sound/programmable-speaker/saw-30.ogg" }},
          { name = "B4",  sound = { filename = "__base__/sound/programmable-speaker/saw-31.ogg" }},
          { name = "C5",  sound = { filename = "__base__/sound/programmable-speaker/saw-32.ogg" }},
          { name = "C#5", sound = { filename = "__base__/sound/programmable-speaker/saw-33.ogg" }},
          { name = "D5",  sound = { filename = "__base__/sound/programmable-speaker/saw-34.ogg" }},
          { name = "D#5", sound = { filename = "__base__/sound/programmable-speaker/saw-35.ogg" }},
          { name = "E5",  sound = { filename = "__base__/sound/programmable-speaker/saw-36.ogg" }}
        }
      },
      {
        name = "square",
        notes =
        {
          { name = "F2",  sound = { filename = "__base__/sound/programmable-speaker/square-01.ogg" }},
          { name = "F#2", sound = { filename = "__base__/sound/programmable-speaker/square-02.ogg" }},
          { name = "G2",  sound = { filename = "__base__/sound/programmable-speaker/square-03.ogg" }},
          { name = "G#2", sound = { filename = "__base__/sound/programmable-speaker/square-04.ogg" }},
          { name = "A2",  sound = { filename = "__base__/sound/programmable-speaker/square-05.ogg" }},
          { name = "A#2", sound = { filename = "__base__/sound/programmable-speaker/square-06.ogg" }},
          { name = "B2",  sound = { filename = "__base__/sound/programmable-speaker/square-07.ogg" }},
          { name = "C3",  sound = { filename = "__base__/sound/programmable-speaker/square-08.ogg" }},
          { name = "C#3", sound = { filename = "__base__/sound/programmable-speaker/square-09.ogg" }},
          { name = "D3",  sound = { filename = "__base__/sound/programmable-speaker/square-10.ogg" }},
          { name = "D#3", sound = { filename = "__base__/sound/programmable-speaker/square-11.ogg" }},
          { name = "E3",  sound = { filename = "__base__/sound/programmable-speaker/square-12.ogg" }},
          { name = "F3",  sound = { filename = "__base__/sound/programmable-speaker/square-13.ogg" }},
          { name = "F#3", sound = { filename = "__base__/sound/programmable-speaker/square-14.ogg" }},
          { name = "G3",  sound = { filename = "__base__/sound/programmable-speaker/square-15.ogg" }},
          { name = "G#3", sound = { filename = "__base__/sound/programmable-speaker/square-16.ogg" }},
          { name = "A3",  sound = { filename = "__base__/sound/programmable-speaker/square-17.ogg" }},
          { name = "A#3", sound = { filename = "__base__/sound/programmable-speaker/square-18.ogg" }},
          { name = "B3",  sound = { filename = "__base__/sound/programmable-speaker/square-19.ogg" }},
          { name = "C4",  sound = { filename = "__base__/sound/programmable-speaker/square-20.ogg" }},
          { name = "C#4", sound = { filename = "__base__/sound/programmable-speaker/square-21.ogg" }},
          { name = "D4",  sound = { filename = "__base__/sound/programmable-speaker/square-22.ogg" }},
          { name = "D#4", sound = { filename = "__base__/sound/programmable-speaker/square-23.ogg" }},
          { name = "E4",  sound = { filename = "__base__/sound/programmable-speaker/square-24.ogg" }},
          { name = "F4",  sound = { filename = "__base__/sound/programmable-speaker/square-25.ogg" }},
          { name = "F#4", sound = { filename = "__base__/sound/programmable-speaker/square-26.ogg" }},
          { name = "G4",  sound = { filename = "__base__/sound/programmable-speaker/square-27.ogg" }},
          { name = "G#4", sound = { filename = "__base__/sound/programmable-speaker/square-28.ogg" }},
          { name = "A4",  sound = { filename = "__base__/sound/programmable-speaker/square-29.ogg" }},
          { name = "A#4", sound = { filename = "__base__/sound/programmable-speaker/square-30.ogg" }},
          { name = "B4",  sound = { filename = "__base__/sound/programmable-speaker/square-31.ogg" }},
          { name = "C5",  sound = { filename = "__base__/sound/programmable-speaker/square-32.ogg" }},
          { name = "C#5", sound = { filename = "__base__/sound/programmable-speaker/square-33.ogg" }},
          { name = "D5",  sound = { filename = "__base__/sound/programmable-speaker/square-34.ogg" }},
          { name = "D#5", sound = { filename = "__base__/sound/programmable-speaker/square-35.ogg" }},
          { name = "E5",  sound = { filename = "__base__/sound/programmable-speaker/square-36.ogg" }}
        }
      },
      {
        name = "celesta",
        notes =
        {
          { name = "F5",  sound = { filename = "__base__/sound/programmable-speaker/celesta-01.ogg" }},
          { name = "F#5", sound = { filename = "__base__/sound/programmable-speaker/celesta-02.ogg" }},
          { name = "G5",  sound = { filename = "__base__/sound/programmable-speaker/celesta-03.ogg" }},
          { name = "G#5", sound = { filename = "__base__/sound/programmable-speaker/celesta-04.ogg" }},
          { name = "A5",  sound = { filename = "__base__/sound/programmable-speaker/celesta-05.ogg" }},
          { name = "A#5", sound = { filename = "__base__/sound/programmable-speaker/celesta-06.ogg" }},
          { name = "B5",  sound = { filename = "__base__/sound/programmable-speaker/celesta-07.ogg" }},
          { name = "C6",  sound = { filename = "__base__/sound/programmable-speaker/celesta-08.ogg" }},
          { name = "C#6", sound = { filename = "__base__/sound/programmable-speaker/celesta-09.ogg" }},
          { name = "D6",  sound = { filename = "__base__/sound/programmable-speaker/celesta-10.ogg" }},
          { name = "D#6", sound = { filename = "__base__/sound/programmable-speaker/celesta-11.ogg" }},
          { name = "E6",  sound = { filename = "__base__/sound/programmable-speaker/celesta-12.ogg" }},
          { name = "F6",  sound = { filename = "__base__/sound/programmable-speaker/celesta-13.ogg" }},
          { name = "F#6", sound = { filename = "__base__/sound/programmable-speaker/celesta-14.ogg" }},
          { name = "G6",  sound = { filename = "__base__/sound/programmable-speaker/celesta-15.ogg" }},
          { name = "G#6", sound = { filename = "__base__/sound/programmable-speaker/celesta-16.ogg" }},
          { name = "A6",  sound = { filename = "__base__/sound/programmable-speaker/celesta-17.ogg" }},
          { name = "A#6", sound = { filename = "__base__/sound/programmable-speaker/celesta-18.ogg" }},
          { name = "B6",  sound = { filename = "__base__/sound/programmable-speaker/celesta-19.ogg" }},
          { name = "C7",  sound = { filename = "__base__/sound/programmable-speaker/celesta-20.ogg" }},
          { name = "C#7", sound = { filename = "__base__/sound/programmable-speaker/celesta-21.ogg" }},
          { name = "D7",  sound = { filename = "__base__/sound/programmable-speaker/celesta-22.ogg" }},
          { name = "D#7", sound = { filename = "__base__/sound/programmable-speaker/celesta-23.ogg" }},
          { name = "E7",  sound = { filename = "__base__/sound/programmable-speaker/celesta-24.ogg" }},
          { name = "F7",  sound = { filename = "__base__/sound/programmable-speaker/celesta-25.ogg" }},
          { name = "F#7", sound = { filename = "__base__/sound/programmable-speaker/celesta-26.ogg" }},
          { name = "G7",  sound = { filename = "__base__/sound/programmable-speaker/celesta-27.ogg" }},
          { name = "G#7", sound = { filename = "__base__/sound/programmable-speaker/celesta-28.ogg" }},
          { name = "A7",  sound = { filename = "__base__/sound/programmable-speaker/celesta-29.ogg" }},
          { name = "A#7", sound = { filename = "__base__/sound/programmable-speaker/celesta-30.ogg" }},
          { name = "B7",  sound = { filename = "__base__/sound/programmable-speaker/celesta-31.ogg" }},
          { name = "C8",  sound = { filename = "__base__/sound/programmable-speaker/celesta-32.ogg" }},
          { name = "C#8", sound = { filename = "__base__/sound/programmable-speaker/celesta-33.ogg" }},
          { name = "D8",  sound = { filename = "__base__/sound/programmable-speaker/celesta-34.ogg" }},
          { name = "D#8", sound = { filename = "__base__/sound/programmable-speaker/celesta-35.ogg" }},
          { name = "E8",  sound = { filename = "__base__/sound/programmable-speaker/celesta-36.ogg" }}
        }
      },
      {
        name = "vibraphone",
        notes =
        {
          { name = "F5",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-01.ogg" }},
          { name = "F#5", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-02.ogg" }},
          { name = "G5",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-03.ogg" }},
          { name = "G#5", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-04.ogg" }},
          { name = "A5",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-05.ogg" }},
          { name = "A#5", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-06.ogg" }},
          { name = "B5",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-07.ogg" }},
          { name = "C6",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-08.ogg" }},
          { name = "C#6", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-09.ogg" }},
          { name = "D6",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-10.ogg" }},
          { name = "D#6", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-11.ogg" }},
          { name = "E6",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-12.ogg" }},
          { name = "F6",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-13.ogg" }},
          { name = "F#6", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-14.ogg" }},
          { name = "G6",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-15.ogg" }},
          { name = "G#6", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-16.ogg" }},
          { name = "A6",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-17.ogg" }},
          { name = "A#6", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-18.ogg" }},
          { name = "B6",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-19.ogg" }},
          { name = "C7",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-20.ogg" }},
          { name = "C#7", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-21.ogg" }},
          { name = "D7",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-22.ogg" }},
          { name = "D#7", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-23.ogg" }},
          { name = "E7",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-24.ogg" }},
          { name = "F7",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-25.ogg" }},
          { name = "F#7", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-26.ogg" }},
          { name = "G7",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-27.ogg" }},
          { name = "G#7", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-28.ogg" }},
          { name = "A7",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-29.ogg" }},
          { name = "A#7", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-30.ogg" }},
          { name = "B7",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-31.ogg" }},
          { name = "C8",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-32.ogg" }},
          { name = "C#8", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-33.ogg" }},
          { name = "D8",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-34.ogg" }},
          { name = "D#8", sound = { filename = "__base__/sound/programmable-speaker/vibraphone-35.ogg" }},
          { name = "E8",  sound = { filename = "__base__/sound/programmable-speaker/vibraphone-36.ogg" }}
        }
      },
      {
        name = "plucked",
        notes =
        {
          { name = "F4",  sound = { filename = "__base__/sound/programmable-speaker/plucked-01.ogg" }},
          { name = "F#4", sound = { filename = "__base__/sound/programmable-speaker/plucked-02.ogg" }},
          { name = "G4",  sound = { filename = "__base__/sound/programmable-speaker/plucked-03.ogg" }},
          { name = "G#4", sound = { filename = "__base__/sound/programmable-speaker/plucked-04.ogg" }},
          { name = "A4",  sound = { filename = "__base__/sound/programmable-speaker/plucked-05.ogg" }},
          { name = "A#4", sound = { filename = "__base__/sound/programmable-speaker/plucked-06.ogg" }},
          { name = "B4",  sound = { filename = "__base__/sound/programmable-speaker/plucked-07.ogg" }},
          { name = "C5",  sound = { filename = "__base__/sound/programmable-speaker/plucked-08.ogg" }},
          { name = "C#5", sound = { filename = "__base__/sound/programmable-speaker/plucked-09.ogg" }},
          { name = "D5",  sound = { filename = "__base__/sound/programmable-speaker/plucked-10.ogg" }},
          { name = "D#5", sound = { filename = "__base__/sound/programmable-speaker/plucked-11.ogg" }},
          { name = "E5",  sound = { filename = "__base__/sound/programmable-speaker/plucked-12.ogg" }},
          { name = "F5",  sound = { filename = "__base__/sound/programmable-speaker/plucked-13.ogg" }},
          { name = "F#5", sound = { filename = "__base__/sound/programmable-speaker/plucked-14.ogg" }},
          { name = "G5",  sound = { filename = "__base__/sound/programmable-speaker/plucked-15.ogg" }},
          { name = "G#5", sound = { filename = "__base__/sound/programmable-speaker/plucked-16.ogg" }},
          { name = "A5",  sound = { filename = "__base__/sound/programmable-speaker/plucked-17.ogg" }},
          { name = "A#5", sound = { filename = "__base__/sound/programmable-speaker/plucked-18.ogg" }},
          { name = "B5",  sound = { filename = "__base__/sound/programmable-speaker/plucked-19.ogg" }},
          { name = "C6",  sound = { filename = "__base__/sound/programmable-speaker/plucked-20.ogg" }},
          { name = "C#6", sound = { filename = "__base__/sound/programmable-speaker/plucked-21.ogg" }},
          { name = "D6",  sound = { filename = "__base__/sound/programmable-speaker/plucked-22.ogg" }},
          { name = "D#6", sound = { filename = "__base__/sound/programmable-speaker/plucked-23.ogg" }},
          { name = "E6",  sound = { filename = "__base__/sound/programmable-speaker/plucked-24.ogg" }},
          { name = "F6",  sound = { filename = "__base__/sound/programmable-speaker/plucked-25.ogg" }},
          { name = "F#6", sound = { filename = "__base__/sound/programmable-speaker/plucked-26.ogg" }},
          { name = "G6",  sound = { filename = "__base__/sound/programmable-speaker/plucked-27.ogg" }},
          { name = "G#6", sound = { filename = "__base__/sound/programmable-speaker/plucked-28.ogg" }},
          { name = "A6",  sound = { filename = "__base__/sound/programmable-speaker/plucked-29.ogg" }},
          { name = "A#6", sound = { filename = "__base__/sound/programmable-speaker/plucked-30.ogg" }},
          { name = "B6",  sound = { filename = "__base__/sound/programmable-speaker/plucked-31.ogg" }},
          { name = "C7",  sound = { filename = "__base__/sound/programmable-speaker/plucked-32.ogg" }},
          { name = "C#7", sound = { filename = "__base__/sound/programmable-speaker/plucked-33.ogg" }},
          { name = "D7",  sound = { filename = "__base__/sound/programmable-speaker/plucked-34.ogg" }},
          { name = "D#7", sound = { filename = "__base__/sound/programmable-speaker/plucked-35.ogg" }},
          { name = "E7",  sound = { filename = "__base__/sound/programmable-speaker/plucked-36.ogg" }}
        }
      },
      {
        name = "steel-drum",
        notes =
        {
          { name = "F3",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-01.ogg" }},
          { name = "F#3", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-02.ogg" }},
          { name = "G3",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-03.ogg" }},
          { name = "G#3", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-04.ogg" }},
          { name = "A3",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-05.ogg" }},
          { name = "A#3", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-06.ogg" }},
          { name = "B3",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-07.ogg" }},
          { name = "C4",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-08.ogg" }},
          { name = "C#4", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-09.ogg" }},
          { name = "D4",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-10.ogg" }},
          { name = "D#4", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-11.ogg" }},
          { name = "E4",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-12.ogg" }},
          { name = "F4",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-13.ogg" }},
          { name = "F#4", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-14.ogg" }},
          { name = "G4",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-15.ogg" }},
          { name = "G#4", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-16.ogg" }},
          { name = "A4",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-17.ogg" }},
          { name = "A#4", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-18.ogg" }},
          { name = "B4",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-19.ogg" }},
          { name = "C5",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-20.ogg" }},
          { name = "C#5", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-21.ogg" }},
          { name = "D5",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-22.ogg" }},
          { name = "D#5", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-23.ogg" }},
          { name = "E5",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-24.ogg" }},
          { name = "F5",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-25.ogg" }},
          { name = "F#5", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-26.ogg" }},
          { name = "G5",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-27.ogg" }},
          { name = "G#5", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-28.ogg" }},
          { name = "A5",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-29.ogg" }},
          { name = "A#5", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-30.ogg" }},
          { name = "B5",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-31.ogg" }},
          { name = "C6",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-32.ogg" }},
          { name = "C#6", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-33.ogg" }},
          { name = "D6",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-34.ogg" }},
          { name = "D#6", sound = { filename = "__base__/sound/programmable-speaker/steel-drum-35.ogg" }},
          { name = "E6",  sound = { filename = "__base__/sound/programmable-speaker/steel-drum-36.ogg" }}
        }
      },

    },

    circuit_connector = circuit_connector_definitions["programmable-speaker"],
    circuit_wire_max_distance = default_circuit_wire_max_distance,
    water_reflection =
    {
      pictures =
      {
        filename = "__base__/graphics/entity/programmable-speaker/programmable-speaker-reflection.png",
        priority = "extra-high",
        width = 12,
        height = 24,
        shift = util.by_pixel(0, 45),
        variation_count = 1,
        scale = 5
      },
      rotate = false,
      orientation_to_variation = false
    }
  },

  {
    type = "power-switch",
    name = "power-switch",
    icon = "__base__/graphics/icons/power-switch.png",
    flags = {"placeable-neutral", "player-creation"},
    minable = {mining_time = 0.2, result = "power-switch"},
    fast_replaceable_group = "power-switch",
    max_health = 200,
    corpse = "power-switch-remnants",
    dying_explosion = "power-switch-explosion",

    collision_box = {{-0.7, -0.7}, {0.7, 0.7}},
    selection_box = {{-1, -1}, {1, 1}},
    damaged_trigger_effect = hit_effects.entity(),

    power_on_animation =
    {
      layers = {
        {
          filename = "__base__/graphics/entity/power-switch/power-switch.png",
          animation_speed = 0.2,
          line_length = 2,
          width = 168,
          height = 138,
          frame_count = 6,
          shift = util.by_pixel(-3, 2),
          scale = 0.5
        },
        {
          filename = "__base__/graphics/entity/power-switch/power-switch-shadow.png",
          animation_speed = 0.2,
          line_length = 2,
          width = 166,
          height = 92,
          frame_count = 6,
          shift = util.by_pixel(6, 14),
          draw_as_shadow = true,
          scale = 0.5
        }
      }
    },
    open_sound = sounds.machine_open,
    close_sound = sounds.machine_close,
    working_sound =
    {
      main_sounds =
      {
        {
          sound = {filename = "__base__/sound/power-switch.ogg", volume = 0.35, audible_distance_modifier = 0.4},
          match_volume_to_activity = true,
          activity_to_volume_modifiers = {offset = 1},
        },
      },
      activate_sound = {variations = sound_variations("__base__/sound/power-switch-activate", 3, 0.3), audible_distance_modifier = 0.4},
      deactivate_sound = {filename = "__base__/sound/power-switch-deactivate.ogg", volume = 0.15, audible_distance_modifier = 0.4},
      max_sounds_per_prototype = 2
    },

    overlay_start_delay = 3, --power on animation overlay is only 2 frames we play at the end
    overlay_start = util.draw_as_glow
    {
      filename = "__base__/graphics/entity/power-switch/power-switch-electricity-start.png",
      blend_mode = "additive",
      animation_speed = 0.2,
      line_length = 2,
      width = 62,
      height = 70,
      frame_count = 2,
      shift = util.by_pixel(2, -4),
      scale = 0.5
    },
    overlay_loop = util.draw_as_glow
    {
      filename = "__base__/graphics/entity/power-switch/power-switch-electricity-loop.png",
      blend_mode = "additive",
      animation_speed = 0.25,
      line_length = 4,
      width = 70,
      height = 60,
      frame_count = 22,
      shift = util.by_pixel(2, -9),
      scale = 0.5
    },
    led_on = util.draw_as_glow
    {
      filename = "__base__/graphics/entity/power-switch/power-switch-led.png",
      x = 48,
      width = 48,
      height = 60,
      shift = util.by_pixel(21, -1),
      blend_mode = "additive",
      scale = 0.5
    },
    led_off = util.draw_as_glow
    {
      filename = "__base__/graphics/entity/power-switch/power-switch-led.png",
      width = 48,
      height = 60,
      shift = util.by_pixel(21, -1),
      blend_mode = "additive",
      scale = 0.5
    },
    circuit_wire_connection_point =
    {
      shadow =
      {
        red   = util.by_pixel(-14, 34+3),
        green = util.by_pixel(-22, 34+3)
      },
      wire =
      {
        red =   util.by_pixel(-17, 26+3),
        green = util.by_pixel(-24, 26+3)
      }
    },
    left_wire_connection_point =
    {
      shadow =
      {
        copper = util.by_pixel(-8, -5+3)
      },
      wire =
      {
        copper = util.by_pixel(-26, -33+3)
      }
    },
    right_wire_connection_point =
    {
      shadow =
      {
        copper = util.by_pixel(45, -3+3)
      },
      wire =
      {
        copper = util.by_pixel(29, -32+3)
      }
    },

    wire_max_distance = 10
  },
  {
    type = "display-panel",
    name = "display-panel",
    icon = "__base__/graphics/icons/display-panel.png",
    icon_size = 64,
    flags = {"player-creation"},
    minable = {mining_time = 0.2, result = "display-panel"},
    max_health = 50,
    corpse = "display-panel-remnants",
    dying_explosion = "display-panel-explosion",
    factoriopedia_simulation = simulations.factoriopedia_display_panel,
    collision_box = {{-0.29, -0.29}, {0.29, 0.29}},
    selection_box = {{-0.5, -0.65}, {0.5, 0.5}},
    open_sound = sounds.machine_open,
    close_sound = sounds.machine_close,
    sprites = make_4way_animation_from_spritesheet({
      layers =
      {
        {
          scale = 0.5,
          filename = "__base__/graphics/entity/display-panel/display-panel.png",
          width = 128,
          height = 128
        },
        {
          scale = 0.5,
          filename = "__base__/graphics/entity/display-panel/display-panel-shadow.png",
          width = 128,
          height = 128,
          draw_as_shadow = true
        }
      }
    }),
    circuit_connector =
    {
      { -- north
        points =
        {
          shadow =
          {
            red = util.by_pixel(-4, -7),
            green = util.by_pixel(19, -7)
          },
          wire =
          {
            red = util.by_pixel(-11, -17.5),
            green = util.by_pixel(12, -17.5)
          }
        }
      },
      { -- east
        points =
        {
          shadow =
          {
            red = util.by_pixel(26, -1),
            green = util.by_pixel(26, 13)
          },
          wire =
          {
            red = util.by_pixel(15, -13.5),
            green = util.by_pixel(18.0, -0.5)
          }
        }
      },
      { -- south
        points =
        {
          shadow =
          {
            red = util.by_pixel(18.5, 16.5),
            green = util.by_pixel(-4, 16.5)
          },
          wire =
          {
            red = util.by_pixel(12, 6),
            green = util.by_pixel(-11, 6)
          }
        }
      },
      { -- west
        points =
        {
          shadow =
          {
            red = util.by_pixel(-11.5, 9.5),
            green = util.by_pixel(-11.5, -4)
          },
          wire =
          {
            red = util.by_pixel(-14.5, -0.5),
            green = util.by_pixel(-17.5, -14)
          }
        }
      }
    },
    circuit_wire_max_distance = default_circuit_wire_max_distance,
    max_text_width = 400,
    text_shift = util.by_pixel(0, -24),
    icon_draw_specification = {shift = util.by_pixel(0.5, -8), scale = 0.5},
    text_color = {1.0, 1.0, 1.0, 1.0},
    background_color = {0.0, 0.0, 0.0, 0.25}
  },
  generate_selector_combinator
  {
    type = "selector-combinator",
    name = "selector-combinator",
    icon = "__base__/graphics/icons/selector-combinator.png",
    flags = {"placeable-neutral", "player-creation"},
    minable = {mining_time = 0.1, result = "selector-combinator"},
    fast_replaceable_group = "selector-combinator",
    max_health = 150,
    corpse = "selector-combinator-remnants",
    dying_explosion = "selector-combinator-explosion",
    collision_box = {{-0.35, -0.65}, {0.35, 0.65}},
    selection_box = {{-0.5, -1}, {0.5, 1}},
    damaged_trigger_effect = hit_effects.entity(),
    icon_draw_specification = {scale = 0.5},

    energy_source =
    {
      type = "electric",
      usage_priority = "secondary-input"
    },
    active_energy_usage = "5kW",

    working_sound =
    {
      sound = {filename = "__base__/sound/combinator.ogg", volume = 0.45, audible_distance_modifier = 0.2},
      fade_in_ticks = 4,
      fade_out_ticks = 20,
      match_speed_to_activity = true
    },
    open_sound = sounds.combinator_open,
    close_sound = sounds.combinator_close,

    activity_led_light =
    {
      intensity = 0,
      size = 1,
      color = {r = 1.0, g = 1.0, b = 1.0}
    },

    activity_led_light_offsets =
    {
      {0.234375, -0.484375},
      {0.5, 0},
      {-0.265625, 0.140625},
      {-0.453125, -0.359375}
    },

    screen_light =
    {
      intensity = 0,
      size = 0.6,
      color = {r = 1.0, g = 1.0, b = 1.0}
    },

    screen_light_offsets =
    {
      {0.015625, -0.234375},
      {0.015625, -0.296875},
      {0.015625, -0.234375},
      {0.015625, -0.296875}
    },

    input_connection_bounding_box = {{-0.5, 0}, {0.5, 1}},
    output_connection_bounding_box = {{-0.5, -1}, {0.5, 0}},

    circuit_wire_max_distance = combinator_circuit_wire_max_distance
  }
}
