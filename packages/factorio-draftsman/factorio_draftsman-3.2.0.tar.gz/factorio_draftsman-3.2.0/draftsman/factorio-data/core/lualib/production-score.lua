local util = require("util")

local function get_total_production_counts(force, item)
  local sum = {}
  for k, surface in pairs(game.surfaces) do
    local production_statistics = item and force.get_item_production_statistics(surface) or force.get_fluid_production_statistics(surface)
    local produced = production_statistics.input_counts
    local consumed = production_statistics.output_counts
    for name, value in pairs (consumed) do
      if produced[name] then
        produced[name] = produced[name] - value
      else
        produced[name] = -value
      end
      if sum[name] then
        sum[name] = sum[name] + produced[name]
      else
        sum[name] = produced[name]
      end
    end
  end
  return sum
end

local function get_raw_resources()
  local raw_resources = {}
  local entities = prototypes.entity
  for name, entity_prototype in pairs (entities) do
    if entity_prototype.resource_category then
      if entity_prototype.mineable_properties and entity_prototype.mineable_properties.products then
        for k, product in pairs (entity_prototype.mineable_properties.products) do
          raw_resources[product.name] = true
        end
      end
    end
  end
  return raw_resources
end

local function get_product_list()
  local product_list = {}
  local recipes = prototypes.recipe

  for recipe_name, recipe_prototype in pairs (recipes) do
    if not recipe_prototype.hidden then
      local ingredients = recipe_prototype.ingredients
      local products = recipe_prototype.products
      for k, product in pairs (products) do
        if not product_list[product.name] then
          product_list[product.name] = {}
        end
        local recipe_ingredients = {}
        local product_amount = util.product_amount(product)
        if product_amount > 0 then
          for j, ingredient in pairs (ingredients) do
            recipe_ingredients[ingredient.name] = ((ingredient.amount)/#products) / product_amount
          end
          recipe_ingredients.energy = (recipe_prototype.energy / #products) / product_amount
          table.insert(product_list[product.name], recipe_ingredients)
        end
      end
    end
  end

  local items = prototypes.item
  local entities = prototypes.entity
  --[[Now we do some tricky stuff for space science type items]]
  local rocket_silos = {}
  for k, entity in pairs (entities) do
    if entity.type == "rocket-silo" and entity.fixed_recipe then
      local recipe = recipes[entity.fixed_recipe]
      if recipe then
        local required_parts = entity.rocket_parts_required
        local list = {}
        for k, product in pairs (recipe.products) do
          local product_amount = util.product_amount(product)
          if product_amount > 0 then
            product_amount = product_amount * required_parts
            list[product.name] = product_amount
          end
        end
        list["energy"] = recipe.energy
        table.insert(rocket_silos, list)
      end
    end
  end

  -- todo use the lua entity prototype to get this if/when its added
  local launch_products = {{type = "item", name = "space-science-pack", amount = 1000, probability = 1}}
  if launch_products then
    for k, launch_product in pairs (launch_products) do
      product_list[launch_product.name] = product_list[launch_product.name] or {}
      local launch_product_amount = util.product_amount(launch_product)
      if launch_product_amount > 0 then
        for k, silo_products in pairs (rocket_silos) do
          local this_silo = {}
          for product_name, product_count in pairs (silo_products) do
            this_silo[product_name] = product_count / launch_product_amount
          end
          this_silo[launch_product.name] = 1 / launch_product_amount
          table.insert(product_list[launch_product.name], this_silo)
        end
      end
    end
  end

  return product_list
end

local default_seed_prices = function()
  return
  {
    ["iron-ore"] = 3.1,
    ["copper-ore"] = 3.6,
    ["coal"] = 3,
    ["stone"] = 2.4,
    ["crude-oil"] = 0.2,
    ["water"] = 1/1000,
    ["steam"] = 1/10000,
    ["wood"] = 3.2,
    ["raw-fish"] = 100,
    ["energy"] = 1,
    ["uranium-ore"] = 8.2,
    ["tungsten-ore"] = 20,
    ["calcite"] = 10,
    ["carbon"] = 10,
    ["holmium-ore"] = 100,
    ["yumako"] = 5,
    ["jellynut"] = 5,
    ["pentapod-egg"] = 10,
    ["biter-egg"] = 50,
    ["spoilage"] = 0.1,

    ["ammoniacal-solution"] = 0.1,
    ["flourine"] = 0.1,
    ["lithium-brine"] = 0.1,
    ["lava"] = 0.1,


  }
end

local default_ingredient_exponent = function() return 1.025 end
local default_raw_resource_price = function() return 2.5 end
local default_resource_ignore = function() return {} end

local default_param = function()
  return
  {
    ingredient_exponent = 1.025, --[[The exponent for increase in value for each additional ingredient formula exponent^#ingredients-2]]
    raw_resource_price = 2.5, --[[If a raw resource isn't given a price, it uses this price]]
    resource_ignore = {} --[[This is used to account for mods removing resource generation, in which case we want the item price to be calculated from recipes.]]
  }
end

local ingredient_multiplier = function(recipe, param)
  return (param.ingredient_exponent or 1) ^ (table_size(recipe) - 2)
end

local deduce_nil_prices = function(price_list, param)
  local nil_prices = {}
  for name, item in pairs (prototypes.item) do
    if not price_list[name] then
      nil_prices[name] = {}
    end
  end
  for name, item in pairs (prototypes.fluid) do
    if not price_list[name] then
      nil_prices[name] = {}
    end
  end
  local recipes = prototypes.recipe
  for name, recipe in pairs (recipes) do
    if not recipe.hidden then
      for k, ingredient in pairs (recipe.ingredients) do
        if nil_prices[ingredient.name] then
          table.insert(nil_prices[ingredient.name], recipe)
        end
      end
    end
  end
  for name, recipes in pairs (nil_prices) do
    if #recipes > 0 then
      local recipe_cost
      local ingredient_amount
      for k, recipe in pairs (recipes) do
        local ingredient_value = 0
        for k, ingredient in pairs (recipe.ingredients) do
          if ingredient.name == name then
            ingredient_amount = ingredient.amount
          else
            local ingredient_price = price_list[ingredient.name]
            if ingredient_price then
              ingredient_value = ingredient_value + (ingredient_price * ingredient.amount)
            else
              ingredient_value = nil
              break
            end
          end
        end
        if not ingredient_value then break end
        local product_value = 0
        for k, product in pairs (recipe.products) do
          local amount = util.product_amount(product)
          local product_price = price_list[product.name]
          if product_price then
            product_value = product_value + product_price * amount
          else
            product_value = nil
            break
          end
        end
        if product_value then
          local reverse_price = (product_value - param.energy_addition(recipe, product_value)) / ingredient_multiplier(recipe.ingredients, param) -- Not perfect, but close enough
          local this_cost = (reverse_price - ingredient_value) / ingredient_amount
          if recipe_cost then
            recipe_cost = math.min(recipe_cost, this_cost)
          else
            recipe_cost = this_cost
          end
        end
      end
      if recipe_cost then
        price_list[name] = param.round(recipe_cost)
      end
    end
  end
end

local ln = math.log
local default_energy_addition = function(recipe, cost)
  return ((ln(recipe.energy + 1) * (cost ^ 0.5)))
end

local default_rounding = function(number)
  return number
end

local production_score = {}

production_score.generate_price_list = function(param)

  local param = param or {}
  local price_list = param.seed_prices or default_seed_prices()

  param.ingredient_exponent = param.ingredient_exponent or default_ingredient_exponent()
  param.raw_resource_price = param.raw_resource_price or default_raw_resource_price()
  param.resource_ignore = param.resource_ignore or default_resource_ignore()
  param.round = param.round or default_rounding
  param.energy_addition = param.energy_addition or default_energy_addition
  param.normalise = param.normalise or function(number) return number end

  local resource_list = get_raw_resources()

  for name, k in pairs (resource_list) do
    if not price_list[name] then
      price_list[name] = param.round(param.raw_resource_price)
    end
  end

  for k, name in pairs (param.resource_ignore or {}) do
    price_list[name] = nil
  end

  local product_list = get_product_list()
  local get_price_recursive
  get_price_recursive = function(name, current_loop, loop_force)
    local price = price_list[name]
    if price then return price end
    price = 0
    if current_loop[name] then
      if loop_force then
        return param.raw_resource_price
      end
      return
    end
    current_loop[name] = true
    local entry = product_list[name]
    if not entry then return end
    local recipe_cost
    for k, recipe in pairs (entry) do

      local this_recipe_cost = 0
      for ingredient_name, cost in pairs (recipe) do
        if ingredient_name ~= "energy" then
          local addition = get_price_recursive(ingredient_name, current_loop, loop_force)
          if addition and addition > 0 then
            this_recipe_cost = this_recipe_cost + (addition * cost)
          else
            this_recipe_cost = 0
            break
          end
        end
      end

      if this_recipe_cost > 0 then
        this_recipe_cost = (this_recipe_cost * ingredient_multiplier(recipe, param)) + param.energy_addition(recipe, this_recipe_cost)
        if recipe_cost then
          recipe_cost = math.min(recipe_cost, this_recipe_cost)
        else
          recipe_cost = this_recipe_cost
        end
      end
    end
    if recipe_cost then
      price = param.round(recipe_cost)
      price_list[name] = price
      return price
    end
  end

  local items = prototypes.item
  for name, item in pairs (items) do
    local current_loop = {}
    get_price_recursive(name, current_loop)
  end

  local fluids = prototypes.fluid
  for name, fluid in pairs (fluids) do
    local current_loop = {}
    get_price_recursive(name, current_loop)
  end

  deduce_nil_prices(price_list, param)
  for name, item in pairs (items) do
    local current_loop = {}
    get_price_recursive(name, current_loop, true)
  end
  for name, fluid in pairs (fluids) do
    local current_loop = {}
    get_price_recursive(name, current_loop, true)
  end
  deduce_nil_prices(price_list, param)

  for k, price in pairs (price_list) do
    price_list[k] = param.normalise(price)
  end

  return price_list
end

production_score.get_production_scores = function(price_list)
  local price_list = price_list or production_score.generate_price_list()
  local scores = {}
  for k, force in pairs (game.forces) do
    local score = 0
    for name, value in pairs (get_total_production_counts(force, true)) do
      local price = price_list[name]
      if price then
        score = score + (price * value)
      end
    end
    for name, value in pairs (get_total_production_counts(force, false)) do
      local price = price_list[name]
      if price then
        score = score + (price * value)
      end
    end
    scores[force.name] = math.floor(score)
  end
  return scores
end

return production_score
