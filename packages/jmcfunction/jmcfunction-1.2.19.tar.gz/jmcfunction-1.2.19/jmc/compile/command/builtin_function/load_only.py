"""Module containing JMCFunction subclasses for custom JMC function that can only be used on load function"""
import json

from ...pack_version import PackVersionFeature
from ...utils import convention_jmc_to_mc
from ..jmc_function_mixin import EventMixin, ItemMixin
from ...tokenizer import Token, TokenType
from ...exception import JMCSyntaxException, JMCMissingValueError, JMCValueError
from ...datapack_data import GUI, SIMPLE_JSON_BODY, GUIMode, Item
from ...datapack import DataPack
from ..utils import ArgType, FormattedText, NumberType, PlayerType, ScoreboardPlayer, hash_string_to_string
from ..jmc_function import JMCFunction, FuncType, func_property
from .._flow_control import parse_switch

from functools import lru_cache


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Predicate.locations",
    arg_type={
        "name": ArgType.STRING,
        "predicate": ArgType.JSON,
        "xMin": ArgType.INTEGER,
        "xMax": ArgType.INTEGER,
        "yMin": ArgType.INTEGER,
        "yMax": ArgType.INTEGER,
        "zMin": ArgType.INTEGER,
        "zMax": ArgType.INTEGER,
    },
    name="predicate_locations"
)
class PredicateLocations(JMCFunction):
    def call(self) -> str:
        predicates = []
        predicate = self.load_arg_json("predicate")
        for x in range(int(self.args["xMin"]), int(self.args["xMax"]) + 1):
            for y in range(int(self.args["yMin"]),
                           int(self.args["yMax"]) + 1):
                for z in range(int(self.args["zMin"]), int(
                        self.args["zMax"]) + 1):
                    predicates.append({
                        "condition": "minecraft:location_check",
                        "offsetX": x,
                        "offsetY": y,
                        "offsetZ": z,
                        "predicate": predicate
                    })

        self.datapack.add_json("predicate", self.args["name"], predicates)
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="RightClick.setup",
    arg_type={
        "idName": ArgType.KEYWORD,
        "functionMap": ArgType.JS_OBJECT
    },
    name="right_click_setup"
)
class RightClickSetup(EventMixin):
    tag_id_var = "__item_id__"

    def call(self) -> str:
        # self.rc_obj = "__rc__" + self.args["idName"][:10]
        func_map = self.datapack.parse_func_map(
            self.raw_args["functionMap"].token, self.tokenizer, self.prefix)
        is_switch = sorted(func_map) == list(range(1, len(func_map) + 1))

        id_name = self.args["idName"]
        if self.is_never_used():
            self.add_event(
                "used:carrot_on_a_stick",
                self.datapack.call_func(
                    self.name,
                    "main"))
            self.make_empty_private_function("main")

        main_func = self.get_private_function("main")

        main_count = self.datapack.get_count(self.name)
        main_func.append(
            f"execute store result score {self.tag_id_var} {DataPack.var_name} run data get entity @s SelectedItem.tag.{id_name}")

        if is_switch:
            func_contents = []
            for func, is_arrow_func in func_map.values():
                if is_arrow_func:
                    func_contents.append(
                        [func]
                    )
                else:
                    func_contents.append(
                        [f"function {self.datapack.namespace}:{func}"])

            main_func.append(
                f"""execute if score {self.tag_id_var} {DataPack.var_name} matches 1.. run {parse_switch(ScoreboardPlayer(
                    PlayerType.SCOREBOARD, (DataPack.var_name, self.tag_id_var)), func_contents, self.datapack, name=self.name)}""")
        else:
            main_func.append(
                f"execute if score {self.tag_id_var} {DataPack.var_name} matches 1.. run {self.datapack.call_func(self.name, main_count)}")
            run = []
            for num, (func, is_arrow_func) in func_map.items():
                if is_arrow_func:
                    run.append(
                        f'execute if score {self.tag_id_var} {DataPack.var_name} matches {num} at @s run {self.datapack.add_raw_private_function(self.name, [func])}')
                else:
                    run.append(
                        f'execute if score {self.tag_id_var} {DataPack.var_name} matches {num} at @s run function {self.datapack.namespace}:{func}')

            self.datapack.add_raw_private_function(self.name, run, main_count)

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Item.create",
    arg_type={
        "itemId": ArgType.KEYWORD,
        "itemType": ArgType.KEYWORD,
        "displayName": ArgType.STRING,
        "lore": ArgType.LIST,
        "nbt": ArgType.JS_OBJECT,
        "component": ArgType.COMPONENT,
    },
    name="item_create",
    defaults={
        "displayName": "",
        "lore": "",
        "nbt": "",
        "component": "",
        "onClick": ""
    }
)
class ItemCreate(ItemMixin, EventMixin):
    def call(self) -> str:
        self.datapack.data.item[self.args["itemId"]
                                ] = self.create_item()

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Item.createUse",
    arg_type={
        "itemId": ArgType.KEYWORD,
        "itemType": ArgType.KEYWORD,
        "displayName": ArgType.STRING,
        "lore": ArgType.LIST,
        "nbt": ArgType.JS_OBJECT,
        "component": ArgType.COMPONENT,
        "onClick": ArgType.FUNC
    },
    name="item_create_use",
    defaults={
        "displayName": "",
        "lore": "",
        "nbt": "",
        "component": "",
        "onClick": ""
    }
)
class ItemCreateUse(ItemMixin, EventMixin):
    rc_obj = {
        "carrot_on_a_stick": "__item_rc_carrot",
        "warped_fungus_on_a_stick": "__item_rc_warped"
    }
    tag_id_var = "__item_id__"
    id_name = "__item_id__"

    def call(self) -> str:
        modify_nbt = None
        item_type = self.args["itemType"]
        on_click = self.args["onClick"]
        if on_click and item_type not in self.rc_obj:
            raise JMCValueError(
                f"on_click can only be used with {
                    ' or '.join(
                        self.rc_obj.keys())}",
                self.raw_args["onClick"].token,
                self.tokenizer,
                suggestion=f"Change item_type to on_click can only be used with {' or '.join(self.rc_obj.keys())}")

        if on_click:
            item_id = self.datapack.data.get_item_id()
            if self.is_never_used():
                self.add_events("used:" + self.args["itemType"], [
                    f"execute store result score {
                        self.tag_id_var} {
                        DataPack.var_name} run data get entity @s SelectedItem.tag.{
                        self.id_name}",
                    f"execute if score {
                        self.tag_id_var} {
                        DataPack.var_name} matches 1.. run {
                        self.datapack.call_func(
                            self.name,
                            'found')}"
                ]
                )
                self.datapack.add_raw_private_function(self.name, [], "found")

            found_func = self.get_private_function("found")

            func = self.args["onClick"]

            if self.raw_args["onClick"].arg_type == ArgType.ARROW_FUNC:
                found_func.append(
                    f'execute if score {self.tag_id_var} {DataPack.var_name} matches {item_id} at @s run {self.datapack.add_raw_private_function(self.name, [func])}')
            else:
                found_func.append(
                    f'execute if score {self.tag_id_var} {DataPack.var_name} matches {item_id} at @s run {func}')

            modify_nbt = {self.id_name: Token.empty(item_id)}

        self.datapack.data.item[self.args["itemId"]
                                ] = self.create_item(modify_nbt=modify_nbt)

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Item.createSpawnEgg",
    arg_type={
        "itemId": ArgType.KEYWORD,
        "mobType": ArgType.KEYWORD,
        "displayName": ArgType.STRING,
        "onPlace": ArgType.FUNC,
        "lore": ArgType.LIST,
        "nbt": ArgType.JS_OBJECT,
        "component": ArgType.COMPONENT
    },
    name="item_create_spawn_egg",
    defaults={
        "displayName": "",
        "lore": "",
        "nbt": "",
        "component": "",
    }
)
class ItemCreateSpawnEgg(EventMixin, ItemMixin):
    def call(self) -> str:
        mob_type = self.args["mobType"]
        spawn_egg = mob_type + "_spawn_egg"
        item_id = self.args["itemId"]
        on_place = self.args["onPlace"]

        self.add_event("used:" + spawn_egg, f"""execute as @e[type=marker,tag=__spawn_egg_{item_id}] at @s run {self.datapack.add_raw_private_function(self.name, [
            "kill @s",
            on_place
        ])}""")

        if self.datapack.version >= PackVersionFeature.COMPONENT:
            modify_component = {"entity_data": Token.empty(
                f"""{{id:"minecraft:marker",Tags:["__spawn_egg_{item_id}"]}}""")}
            self.datapack.data.item[self.args["itemId"]] = self.create_item(
                modify_component=modify_component)

        else:
            modify_nbt = {"EntityTag": Token.empty(
                f"""{{id:"minecraft:marker",Tags:["__spawn_egg_{item_id}"]}}""")}
            self.datapack.data.item[self.args["itemId"]] = self.create_item(
                modify_nbt=modify_nbt)
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Item.createSign",
    arg_type={
        "itemId": ArgType.KEYWORD,
        "variant": ArgType.KEYWORD,
        "displayName": ArgType.STRING,
        "lore": ArgType.LIST,
        "texts": ArgType.LIST,
        "nbt": ArgType.JS_OBJECT,
        "component": ArgType.COMPONENT,
        "onClick": ArgType.FUNC,
        "isFrontGlow": ArgType.KEYWORD,
        "isBackGlow": ArgType.KEYWORD
    },
    name="item_create_sign",
    defaults={
        "displayName": "",
        "lore": "",
        "texts": "",
        "nbt": "",
        "component": "",
        "onClick": "",
        "isFrontGlow": "false",
        "isBackGlow": "false"
    }
)
class ItemCreateSign(ItemMixin):
    _VARIANTS = {"oak", "spruce", "birch", "jungle",
                 "acacia", "dark_oak", "crimson", "warped",
                 "mangrove", "bamboo", "cherry", "pale_oak"}

    def call(self) -> str:
        variant = self.args["variant"]
        is_front_glow = self.check_bool("isFrontGlow")
        is_back_glow = self.check_bool("isBackGlow")
        if is_front_glow:
            self.datapack.version.require(
                PackVersionFeature.SIGN_BACK_TEXT, self.raw_args["isFrontGlow"].token, self.tokenizer)
        if is_back_glow:
            self.datapack.version.require(
                PackVersionFeature.SIGN_BACK_TEXT, self.raw_args["isBackGlow"].token, self.tokenizer)
        if variant not in self._VARIANTS:
            raise JMCValueError(
                f"Unrecognized wood variant for sign ({variant})",
                self.raw_args["variant"].token,
                self.tokenizer,
                suggestion=f"Available variants are {' '.join(repr(i) for i in self._VARIANTS)}")

        self.args["itemType"] = variant + "_sign"
        on_click = self.args["onClick"]
        if self.args["texts"]:
            texts, texts_tokens = self.datapack.parse_list(
                self.raw_args["texts"].token, self.tokenizer, TokenType.STRING)
        else:
            texts = []
            texts_tokens = []

        if is_front_glow and len(texts) == 0:
            raise JMCValueError(
                f"'isFrontGlow' is 'true' but there's no text in front of the sign",
                self.raw_args["isFrontGlow"].token,
                self.tokenizer,
            )
        if is_back_glow and len(texts) <= 4:
            raise JMCValueError(
                f"'isBackGlow' is 'true' but there's no text in the back of the sign",
                self.raw_args["isBackGlow"].token,
                self.tokenizer,
            )
        if self.datapack.version >= PackVersionFeature.SIGN_BACK_TEXT:
            if len(texts) > 8:
                raise JMCValueError(
                    f"Sign may only have 8 lines of text (got {len(texts)})",
                    self.raw_args["texts"].token,
                    self.tokenizer, suggestion="4 lines for the front and 4 lines for the back")
        else:
            if len(texts) > 4:
                raise JMCValueError(
                    f"Sign may only have 4 lines of text (got {len(texts)})",
                    self.raw_args["texts"].token,
                    self.tokenizer)
        has_back_text = len(texts) > 4
        if has_back_text:
            texts.extend([''] * (8 - len(texts)))
            texts_tokens.extend([Token.empty()] * (8 - len(texts_tokens)))
        else:
            texts.extend([''] * (4 - len(texts)))
            texts_tokens.extend([Token.empty()] * (4 - len(texts_tokens)))

        formatted_texts_ = [FormattedText(text, text_token, self.tokenizer, self.datapack) if text else FormattedText.empty(self.tokenizer, self.datapack)
                            for text, text_token in zip(texts, texts_tokens)]
        if on_click:
            if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
                outer_key, inner_key = "clickEvent", "value"
            else:
                outer_key, inner_key = "click_event", "command"
            formatted_texts_[0].add_key(
                outer_key, {
                    "action": "run_command", inner_key: on_click})
            if not formatted_texts_[0]:
                formatted_texts_[0].add_key("text", "")

        repr_ = (
            lambda x: x) if self.datapack.version >= PackVersionFeature.TEXT_COMPONENT else repr
        texts_ = [repr_(str(text)) for text in formatted_texts_]

        front_glow = "has_glowing_text:1b," if is_front_glow else ""
        if has_back_text:
            back_texts_ = texts_[4:]
            del texts_[4:]
            back_glow = "has_glowing_text:1b," if is_back_glow else ""
            back_text = f""",back_text:{{{back_glow}messages:[{
                ','.join(back_texts_)}]}}"""
        else:
            back_text = ""
        if self.datapack.version >= PackVersionFeature.COMPONENT:
            modify_component = {"entity_data": Token.empty(
                f"""{{id:"sign",front_text:{{{front_glow}messages:[{','.join(texts_)}]}}{back_text}}}""")}
            self.datapack.data.item[self.args["itemId"]] = self.create_item(
                modify_component=modify_component)

        else:
            if self.datapack.version >= PackVersionFeature.SIGN_BACK_TEXT:
                modify_nbt = {"BlockEntityTag": Token.empty(
                    f"""{{front_text:{{{front_glow}messages:[{','.join(texts_)}]}}{back_text}}}""")}
                self.datapack.data.item[self.args["itemId"]] = self.create_item(
                    modify_nbt=modify_nbt)
            else:
                modify_nbt = {"BlockEntityTag": Token.empty(
                    f"""{{Text1:{texts_[0]},Text2:{texts_[1]},Text3:{texts_[2]},Text4:{texts_[3]}}}""")}
                self.datapack.data.item[self.args["itemId"]] = self.create_item(
                    modify_nbt=modify_nbt)

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Player.onEvent",
    arg_type={
        "criteria": ArgType.KEYWORD,
        "function": ArgType.FUNC,
    },
    name="player_on_event"
)
class PlayerOnEvent(EventMixin):
    def call(self) -> str:
        self.add_event(self.args['criteria'], self.args['function'])
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Trigger.setup",
    arg_type={
        "objective": ArgType.KEYWORD,
        "triggers": ArgType.JS_OBJECT
    },
    name="trigger_setup",
    ignore={
        "triggers"
    }
)
class TriggerSetup(JMCFunction):
    def call(self) -> str:
        func_map = self.datapack.parse_func_map(
            self.raw_args["triggers"].token, self.tokenizer, self.prefix)
        is_switch = sorted(func_map) == list(range(1, len(func_map) + 1))

        obj = self.args["objective"]
        self.datapack.add_objective(obj, "trigger")
        if self.is_never_used():
            self.datapack.add_tick_command(
                self.datapack.call_func(self.name, "main"))
            self.make_empty_private_function("main")
            self.datapack.add_load_command(
                f"execute as @a run {self.datapack.call_func(self.name, 'enable')}")
            self.make_empty_private_function("enable")

            self.datapack.add_private_json("advancements", f"{self.name}/enable", {
                "criteria": {
                    "requirement": {
                        "trigger": "minecraft:tick"
                    }
                },
                "rewards": {
                    "function": f"{self.datapack.namespace}:{DataPack.private_name}/{self.name}/enable"
                }
            })

        main_func = self.get_private_function("main")
        self.get_private_function("enable").append(
            f"scoreboard players enable @s {obj}")

        main_count = self.datapack.get_count(self.name)
        main_func.append(
            f"execute as @a[scores={{{obj}=1..}}] at @s run {self.datapack.call_func(self.name, main_count)}")

        if is_switch:
            func_contents = []
            for func, is_arrow_func in func_map.values():
                if is_arrow_func:
                    func_contents.append(
                        [func]
                    )
                else:
                    func_contents.append(
                        [f"function {self.datapack.namespace}:{func}"])
            run = [
                parse_switch(ScoreboardPlayer(
                    PlayerType.SCOREBOARD, (obj, "@s")), func_contents, self.datapack, self.name),
            ]
        else:
            run = []
            for num, (func, is_arrow_func) in func_map.items():
                if is_arrow_func:
                    run.append(
                        f'execute if score @s {obj} {DataPack.var_name} matches {num} run {self.datapack.add_raw_private_function(self.name, [func])}')
                else:
                    run.append(
                        f'execute if score @s {obj} {DataPack.var_name} matches {num} run {func}')

        run.extend([f"scoreboard players set @s {obj} 0",
                    f"scoreboard players enable @s {obj}"])
        self.datapack.add_raw_private_function(self.name, run, main_count)

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Trigger.add",
    arg_type={
        "objective": ArgType.KEYWORD,
        "function": ArgType.FUNC
    },
    name="trigger_add",
)
class TriggerAdd(JMCFunction):
    def call(self) -> str:

        obj = self.args["objective"]
        self.datapack.add_objective(obj, "trigger")
        if self.is_never_used():
            self.datapack.add_tick_command(
                self.datapack.call_func(self.name, "main"))
            self.make_empty_private_function("main")
            self.datapack.add_load_command(
                f"execute as @a run {self.datapack.call_func(self.name, 'enable')}")
            self.make_empty_private_function("enable")

            self.datapack.add_private_json("advancements", f"{self.name}/enable", {
                "criteria": {
                    "requirement": {
                        "trigger": "minecraft:tick"
                    }
                },
                "rewards": {
                    "function": f"{self.datapack.namespace}:{DataPack.private_name}/{self.name}/enable"
                }
            })

        main_func = self.get_private_function("main")
        self.get_private_function("enable").append(
            f"scoreboard players enable @s {obj}")

        func = self.args["function"]
        run = f"""execute as @a[scores={{{obj}=1..}}] at @s run {self.datapack.add_raw_private_function(self.name, [
            func,
            f"scoreboard players set @s {obj} 0",
            f"scoreboard players enable @s {obj}"
        ], obj)}"""
        main_func.append(run)

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Timer.add",
    arg_type={
        "objective": ArgType.KEYWORD,
        "mode": ArgType.KEYWORD,
        "selector": ArgType.SELECTOR,
        "function": ArgType.FUNC
    },
    name="timer_add",
    defaults={
        "function": ""
    }
)
class TimerAdd(JMCFunction):
    def call(self) -> str:
        mode = self.args["mode"]
        obj = self.args["objective"]
        selector = self.args["selector"]
        if mode not in {"runOnce", "runTick", "none"}:
            raise JMCSyntaxException(
                f"Avaliable modes for {self.call_string} are 'runOnce', 'runTick' and 'none' (got '{mode}')", self.raw_args["mode"].token, self.tokenizer, suggestion="'runOnce' run the commands once after the timer is over.\n'runTick' run the commands every tick if timer is over.\n'none' do not run any command.")

        if mode in {"runOnce",
                    "runTick"} and ("function" not in self.raw_args):
            raise JMCMissingValueError("function", self.token, self.tokenizer)
        if mode == "none" and "function" in self.raw_args:
            raise JMCSyntaxException(
                f"'function' is provided in 'none' mode {self.call_string}", self.raw_args["function"].token, self.tokenizer)
        self.datapack.add_objective(obj)
        if self.is_never_used():
            self.datapack.add_tick_command(
                self.datapack.call_func(self.name, "main"))
            self.make_empty_private_function("main")

        main_func = self.get_private_function("main")
        if selector.startswith("@"):
            if_selector = f"as {selector} if score @s"
            unless_selector = f"as {selector} unless score @s"
            at_s = "@s"
            at_at_s = "at @s "
        else:
            if_selector = f"if score {selector}"
            unless_selector = f"unless score {selector}"
            at_s = selector
            at_at_s = ""
        main_func.append(
            f"execute {if_selector} {obj} matches 0.. run scoreboard players remove {at_s} {obj} 1")
        if mode == "runOnce":
            count = self.datapack.get_count(self.name)
            main_func.append(
                f"""execute {if_selector} {obj} matches 0 {at_at_s}run {self.datapack.add_private_function(
                    self.name,
                    self.args["function"],
                    count
                )}""")
        elif mode == "runTick":
            count = self.datapack.get_count(self.name)
            main_func.append(
                f"""execute {unless_selector} {obj} matches 1.. {at_at_s}run {self.datapack.add_private_function(
                    self.name,
                    self.args["function"],
                    count
                )}""")

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Recipe.table",
    arg_type={
        "recipe": ArgType.JSON,
        "baseItem": ArgType.KEYWORD,
        "onCraft": ArgType.FUNC
    },
    name="recipe_table",
    defaults={
        "baseItem": "minecraft:knowledge_book",
        "onCraft": ""
    }
)
class RecipeTable(JMCFunction):
    def call(self) -> str:
        base_item = self.args["baseItem"]
        if not base_item.startswith("minecraft:"):
            base_item = "minecraft:" + base_item
        count = self.datapack.get_count(self.name)
        self.datapack.add_private_json('advancements', f'{self.name}/{count}', {
            "criteria": {
                "requirement": {
                    "trigger": "minecraft:recipe_unlocked",
                    "conditions": {
                        "recipe": f"{self.datapack.namespace}:{DataPack.private_name}/{self.name}/{count}"
                    }
                }
            },
            "rewards": {
                "function": f"{self.datapack.namespace}:{DataPack.private_name}/{self.name}/{count}"
            }
        })

        json = self.load_arg_json("recipe")

        # raise JMCSyntaxException("'result' key not found in recipe",
        # self.raw_args["recipe"].token, self.tokenizer,
        # display_col_length=True, suggestion="recipe json maybe invalid")
        if "result" in json:
            if "item" not in json["result"]:
                raise JMCSyntaxException("'item' key not found in 'result' in recipe",
                                         self.raw_args["recipe"].token, self.tokenizer, display_col_length=True, suggestion="recipe json maybe invalid")
            if "count" not in json["result"]:
                raise JMCSyntaxException("'count' key not found in 'result' in recipe",
                                         self.raw_args["recipe"].token, self.tokenizer, display_col_length=True, suggestion="recipe json maybe invalid")

            result_item = json["result"]["item"]
            json["result"]["item"] = base_item
            result_count = json["result"]["count"]
            json["result"]["count"] = 1
            result_command = f"give @s {result_item} {result_count}"
        else:
            result_command = ""

        self.datapack.add_private_json(
            "recipes", f"{self.name}/{count}", json)
        self.datapack.add_raw_private_function(
            self.name,
            [
                f"clear @s {base_item} 1",
                result_command,
                f"recipe take @s {
                    self.datapack.namespace}:{
                    DataPack.private_name}/{
                    self.name}/{count}",
                f"advancement revoke @s only {
                    self.datapack.namespace}:{
                    DataPack.private_name}/{
                    self.name}/{count}",
                self.args["onCraft"]
            ],
            count
        )
        return ""


GUI_OBJ_NAME = "__gui__"


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="GUI.template",
    arg_type={
        "name": ArgType.KEYWORD,
        "template": ArgType.LIST,
        "mode": ArgType.KEYWORD
    },
    name="gui_template"
)
class GUITemplate(JMCFunction):
    MODE_MAP: dict[str, GUIMode] = {
        "entity": GUIMode.ENTITY,
        "block": GUIMode.BLOCK,
        "enderchest": GUIMode.ENDERCHEST
    }

    def call(self) -> str:
        template, _ = self.datapack.parse_list(
            self.raw_args["template"].token, self.tokenizer, TokenType.STRING)
        name = convention_jmc_to_mc(
            self.raw_args["name"].token, self.tokenizer, self.prefix)
        mode_str = self.args["mode"]
        if mode_str not in self.MODE_MAP:
            raise JMCValueError(
                f"Unrecognized mode for {self.call_string}",
                self.raw_args["mode"].token,
                self.tokenizer,
                suggestion=f"""Available modes are {', '.join("'" + mode_ + "'" for mode_ in self.MODE_MAP.keys())}""")
        if name in self.datapack.data.guis:
            raise JMCValueError(
                f"GUI Template '{name}' was already defined",
                self.raw_args["name"].token,
                self.tokenizer)
        mode = self.MODE_MAP[mode_str]
        self.datapack.data.guis[name] = GUI(
            name, mode, template)
        if self.is_never_used():
            self.datapack.add_load_command(
                f"data modify storage {self.datapack.namespace}:{self.datapack.storage_name} GUI set value {{}}")
        self.datapack.add_raw_private_function(f"gui/{name}", [
            f"""execute if entity @p[distance=..8] run {
                self.datapack.add_raw_private_function(f"gui/{name}", [
                    f"data modify storage {
                        self.datapack.namespace}:{
                        self.datapack.storage_name} GUI.Items set from {
                        mode.value[1]} {
                        mode.value[2]}",
                    f"execute store result score __gui__.item_count {
                        self.datapack.var_name} if data storage {
                        self.datapack.namespace}:{
                        self.datapack.storage_name} GUI.Items[].tag.__gui__",
                    f'execute if score __gui__.item_count {
                        self.datapack.var_name} matches 0 run {
                        self.datapack.call_func(
                            f"gui/{name}", "reset")}'
                ], "active")
            }""",
            "execute if block ~ ~-1 ~ hopper run data merge block ~ ~-1 ~ {TransferCooldown:20d}" if mode ==
            GUIMode.BLOCK else ""
        ], "run")
        self.datapack.add_raw_private_function(
            f"gui/{name}", [
                f"scoreboard players reset * {GUI_OBJ_NAME}"
            ], "container_changed")

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="GUI.registers",
    arg_type={
        "name": ArgType.KEYWORD,
        "id": ArgType.STRING,
        "items": ArgType.LIST,
        "variable": ArgType.SCOREBOARD,
        "onClick": ArgType.FUNC,
        "onClickAsGUI": ArgType.FUNC
    },
    name="gui_registers",
    defaults={
        "onClick": "",
        "onClickAsGUI": ""
    }
)
class GUIRegisters(ItemMixin):
    def call(self) -> str:
        name = convention_jmc_to_mc(
            self.raw_args["name"].token, self.tokenizer, self.prefix)
        if name not in self.datapack.data.guis:
            raise JMCValueError(
                f"GUI Template '{name}' was never defined",
                self.raw_args["name"].token,
                self.tokenizer)

        if len(self.args["id"]) != 1:
            raise JMCValueError(
                f"'id' expected 1 charater (got {len(self.args['id'])})",
                self.raw_args["id"].token,
                self.tokenizer)

        item_strings, item_strings_tokens = self.datapack.parse_list(self.raw_args["items"].token,
                                                                     self.tokenizer, TokenType.KEYWORD)
        if not item_strings:
            raise JMCValueError(
                "GUI Template expected non-empty 'items' argument",
                self.raw_args["items"].token,
                self.tokenizer)

        items: list[Item] = []

        if self.args["onClick"]:
            on_click = self.datapack.add_private_function(
                f"gui/{name}/on_click", self.args["onClick"])
            interactive_id = self.datapack.get_count(
                f"{self.name}/{name}")
            for item_str, item_str_token in zip(
                    item_strings, item_strings_tokens):
                if item_str not in self.datapack.data.item:
                    raise JMCValueError(
                        f'Item id: \'{item_str}\' is not defined.',
                        self.raw_args["items"].token,
                        self.tokenizer,
                        suggestion=f"Use Item.create to make this item BEFORE using {
                            self.call_string}"
                    )
                items.append(self.clone_item(self.datapack.data.item[item_str], modify_nbt={
                    "__gui__": Token.empty(f"{{interactive_id:{interactive_id},name:{repr(name)}}}")}, error_token=item_str_token))

            self.set_items(
                name,
                self.args["id"],
                items,
                self.raw_args["id"].token,
                interactive_id,
                on_click)
        else:
            for item_str, item_str_token in zip(
                    item_strings, item_strings_tokens):
                if item_str not in self.datapack.data.item:
                    raise JMCValueError(
                        f'Item id: \'{item_str}\' is not defined.',
                        self.raw_args["items"].token,
                        self.tokenizer,
                        suggestion=f"Use Item.create to make this item BEFORE using {
                            self.call_string}"
                    )
                items.append(self.clone_item(self.datapack.data.item[item_str], modify_nbt={
                    "__gui__": Token.empty(f"{{name:{repr(name)}}}")}, error_token=item_str_token))
            self.set_items(
                name,
                self.args["id"],
                items,
                self.raw_args["id"].token)

        return ""

    def set_items(self, name: str, slot: str, items: list[Item], token: Token,
                  interactive_id: str | None = None, on_click: str = "") -> None:
        gui = self.datapack.data.guis[name]
        for item in items:
            if item.item_type == "air":
                raise JMCValueError(
                    "Item cannot be air",
                    token,
                    self.tokenizer)
            gui.item_types.add(item.item_type)

        for template_item in gui.template_map[slot]:
            if template_item.items is not gui.default_item:
                raise JMCValueError(
                    f"This id ({slot}) was already registered in {name} template",
                    token,
                    self.tokenizer)
            if template_item.variable is not None:
                raise JMCValueError(
                    f"This id ({slot}) was already registered as registers in {name} template",
                    self.raw_args["id"].token,
                    self.tokenizer)
            template_item.items = items
            template_item.interactive_id = interactive_id
            template_item.on_click = on_click
            template_item.variable = self.args["variable"]
            if self.args["onClickAsGUI"]:
                template_item.container_changed = [self.args["onClickAsGUI"]]


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="GUI.register",
    arg_type={
        "name": ArgType.KEYWORD,
        "id": ArgType.STRING,
        "item": ArgType.KEYWORD,
        "displayName": ArgType.STRING,
        "lore": ArgType.LIST,
        "nbt": ArgType.JS_OBJECT,
        "onClick": ArgType.FUNC,
        "onClickAsGUI": ArgType.FUNC
    },
    name="gui_register",
    defaults={
        "displayName": "",
        "lore": "",
        "nbt": "",
        "onClick": "",
        "onClickAsGUI": ""
    }
)
class GUIRegister(ItemMixin):
    def call(self) -> str:
        name = convention_jmc_to_mc(
            self.raw_args["name"].token, self.tokenizer, self.prefix)
        if name not in self.datapack.data.guis:
            raise JMCValueError(
                f"GUI Template '{name}' was never defined",
                self.raw_args["name"].token,
                self.tokenizer)

        if len(self.args["id"]) != 1:
            raise JMCValueError(
                f"'id' expected 1 charater (got {len(self.args['id'])})",
                self.raw_args["id"].token,
                self.tokenizer)
        if self.args["onClick"]:
            on_click = self.datapack.add_private_function(
                f"gui/{name}/on_click", self.args["onClick"])
            interactive_id = self.datapack.get_count(
                f"{self.name}/{name}")

            self.set_item(
                name,
                self.args["id"],
                self.create_item(
                    item_type_param="item",
                    modify_nbt={"__gui__": Token.empty(f"{{interactive_id:{interactive_id},name:{repr(name)}}}")}),
                self.raw_args["id"].token,
                interactive_id,
                on_click)

        else:
            self.set_item(
                name,
                self.args["id"],
                self.create_item(
                    item_type_param="item",
                    modify_nbt={"__gui__": Token.empty(f"{{name:{repr(name)}}}")}),
                self.raw_args["id"].token)

        return ""

    def set_item(self, name: str, slot: str, item: Item, token: Token,
                 interactive_id: str | None = None, on_click: str = "") -> None:
        gui = self.datapack.data.guis[name]
        if item.item_type != "air":
            gui.item_types.add(item.item_type)
        for template_item in gui.template_map[slot]:
            if template_item.items is not gui.default_item:
                raise JMCValueError(
                    f"This id ({slot}) was already registered in {name} template",
                    token,
                    self.tokenizer)
            if template_item.variable is not None:
                raise JMCValueError(
                    f"This id ({slot}) was already registered as registers in {name} template",
                    self.raw_args["id"].token,
                    self.tokenizer)
            template_item.items = item if item.item_type != "air" else None
            template_item.interactive_id = interactive_id
            template_item.on_click = on_click
            if self.args["onClickAsGUI"]:
                template_item.container_changed = [self.args["onClickAsGUI"]]


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="GUI.create",
    arg_type={
        "name": ArgType.KEYWORD,
    },
    name="gui_create"
)
class GUICreate(JMCFunction):

    def call(self) -> str:
        name = convention_jmc_to_mc(
            self.raw_args["name"].token, self.tokenizer, self.prefix)
        if name not in self.datapack.data.guis:
            raise JMCValueError(
                f"GUI Template '{name}' was never defined",
                self.raw_args["name"].token,
                self.tokenizer)

        if self.is_never_used():
            self.datapack.add_objective(GUI_OBJ_NAME)
            self.datapack.add_raw_private_function("__gui__", [
                f"execute store result score $UUID0_P {GUI_OBJ_NAME} run data get entity @s UUID[0]",
                f"execute store result score $UUID1_P {GUI_OBJ_NAME} run data get entity @s UUID[1]",
                f"execute store result score $UUID2_P {GUI_OBJ_NAME} run data get entity @s UUID[2]",
                f"execute store result score $UUID3_P {GUI_OBJ_NAME} run data get entity @s UUID[3]",
                f"execute if score $UUID0_P {GUI_OBJ_NAME} = $UUID0_E {GUI_OBJ_NAME} if score $UUID1_P {GUI_OBJ_NAME} = $UUID1_E {GUI_OBJ_NAME} if score $UUID2_P {GUI_OBJ_NAME} = $UUID2_E {GUI_OBJ_NAME} if score $UUID3_P {GUI_OBJ_NAME} = $UUID3_E {GUI_OBJ_NAME} run tag @s add __gui__.clicker"
            ], "compare_player_uuid")

            self.datapack.add_raw_private_function("__gui__", [
                f"execute store result score $UUID0_E {GUI_OBJ_NAME} run data get entity @s Thrower[0]",
                f"execute store result score $UUID1_E {GUI_OBJ_NAME} run data get entity @s Thrower[1]",
                f"execute store result score $UUID2_E {GUI_OBJ_NAME} run data get entity @s Thrower[2]",
                f"execute store result score $UUID3_E {GUI_OBJ_NAME} run data get entity @s Thrower[3]",
            ], "copy_item_owner")

            self.datapack.add_raw_private_function(
                "__gui__", [
                    "data modify entity @s Owner set from entity @p[tag=__gui__.clicker] UUID",
                    "tp @s @p[tag=__gui__.clicker]"
                ], "return_item"
            )

        return_item = self.datapack.call_func("__gui__", "return_item")
        copy_item_owner = self.datapack.call_func("__gui__", "copy_item_owner")
        compare_player_uuid = self.datapack.call_func(
            "__gui__", "compare_player_uuid")

        container_changed = self.datapack.private_functions[f"gui/{name}"]["container_changed"]
        gui = self.datapack.data.guis[name]
        if gui.is_created:
            raise JMCValueError(
                f"GUI '{name}' was already created",
                self.raw_args["name"].token,
                self.tokenizer)
        gui.is_created = True

        self.datapack.private_functions[f"gui/{name}"]["active"].append(
            f'execute unless score __gui__.item_count {self.datapack.var_name} matches 0 unless score __gui__.item_count {self.datapack.var_name} matches {gui.length} run {self.datapack.call_func(f"gui/{name}", "container_changed")}')
        self.datapack.add_private_json(
            "tags/items", f"gui/{name}", {"values": list(gui.item_types)})
        item_tags = f"#{
            self.datapack.namespace}:{
            self.datapack.private_name}/gui/{name}"

        reset_commands = gui.get_reset_commands()
        # reset_commands.append("kill @e[type=minecraft:item,nbt={Item:{tag:{__gui__:{name:%s}}}}]" % repr(
        #     name),)
        reset = self.datapack.add_raw_private_function(
            f"gui/{name}", reset_commands, "reset")

        for index, template_item in enumerate(gui.template):
            if template_item.items is None:
                continue
            on_change = self.datapack.add_raw_private_function(
                f"gui/{name}/container_changed", [
                    f"execute store result score $is_item {GUI_OBJ_NAME} if data storage {
                        self.datapack.namespace}:{
                        self.datapack.storage_name} GUI.Items[{{Slot:{index}b}}]",
                    # Find player with gui item
                    # fmt: off
                    f"execute as @a[distance=..10] store result score @s {GUI_OBJ_NAME} run clear @s {item_tags}{{__gui__: {{name: {repr(name)}}}}}",
                    # fmt: on
                    # Tag player with gui item as clicker
                    f"tag @p[scores={{{GUI_OBJ_NAME}=1..}}] add __gui__.clicker",
                    # Check if clicker is found
                    f"execute if entity @p[tag=__gui__.clicker] run scoreboard players set $is_click {GUI_OBJ_NAME} 1",
                    # If there's no clicker
                    "execute unless score $is_click %s matches 1 as @e[type=item,nbt={Item:{tag:{__gui__:{name:%s}}}},limit=1] run %s" % (
                        GUI_OBJ_NAME, repr(name), copy_item_owner),
                    f"execute unless score $is_click {GUI_OBJ_NAME} matches 1 as @a[distance=..8] run {compare_player_uuid}",
                    # Summon dummy item
                    'execute if score $is_item %s matches 1 run summon item ~ ~256 ~ {Item: {id:"minecraft:stone",Count:1b},Tags:["__gui__.%s.dropped_item"]}' % (
                        GUI_OBJ_NAME, name),
                    f"data modify entity @e[limit=1,type=item,tag=__gui__.{name}.dropped_item] Item set from storage {
                        self.datapack.namespace}:{
                        self.datapack.storage_name} GUI.Items[{{Slot:{index}b}}]",
                    f"execute if score $is_item {GUI_OBJ_NAME} matches 1 as @e[limit=1,type=item,tag=__gui__.{name}.dropped_item] run {return_item}",
                    f"""execute as @p[tag=__gui__.clicker] at @s run {
                        template_item.on_click}""" if template_item.interactive_id is not None else "",
                    *template_item.container_changed
                ])
            container_changed.append(
                f"execute unless data storage {self.datapack.namespace}:{self.datapack.storage_name} GUI.Items[{{Slot:{index}b,tag:{{__gui__:{{name:{repr(name)}}}}}}}] run {on_change}")

        container_changed.extend([
            "kill @e[type=minecraft:item,nbt={Item:{tag:{__gui__:{name:%s}}}}]" % repr(
                name),
            "tag @a remove __gui__.clicker",
            reset])

        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Team.add",
    arg_type={
        "team": ArgType.KEYWORD,
        "displayName": ArgType.STRING,
        "properties": ArgType.JS_OBJECT
    },
    name="team_add",
    defaults={
        "displayName": "",
        "properties": "",
    }
)
class TeamAdd(JMCFunction):
    def call(self) -> str:
        command = f'team add {self.args["team"]}'
        if self.args["team"] in self.datapack.data.teams:
            team = self.datapack.data.teams[self.args["team"]]
            raise JMCValueError(
                f"Team {self.args['team']} was already defined",
                self.raw_args["team"].token,
                self.tokenizer, suggestion=f"It was defined at line {team[1].line} col {team[1].col}")
        self.datapack.data.teams[self.args["team"]] = (
            self.args["displayName"], self.raw_args["team"].token)
        if self.args["displayName"]:
            command += ' ' + self.format_text("displayName")

        properties = self.tokenizer.parse_js_obj(
            self.raw_args["properties"].token) if self.args["properties"] else {}
        for key, value in properties.items():
            command += f"\nteam modify {
                self.args['team']} {key} {
                value.string}"

        return command


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProp.clickCommand",
    arg_type={
        "propertyName": ArgType.STRING,
        "function": ArgType.ARROW_FUNC,
        "local": ArgType.KEYWORD
    },
    name="text_prop_click_command",
    defaults={
        "local": "false"
    },
    ignore={
        "function",
    }
)
class TextPropClickCommand(JMCFunction):
    def call(self) -> str:
        command = self.datapack.parse_function_token(
            self.raw_args["function"].token,
            self.tokenizer, self.prefix)
        if not command:
            raise JMCValueError(
                "Unexpected empty arrow function",
                self.raw_args["function"].token,
                self.tokenizer)
        if len(command) > 1:
            raise JMCValueError(
                f"'{
                    self.call_string}' only allows 1 command (got {
                    len(command)})",
                self.raw_args["function"].token,
                self.tokenizer)
        if command[0].startswith("say"):
            raise JMCValueError(
                f"'{self.call_string}' doesn't allow 'say' command",
                self.raw_args["function"].token,
                self.tokenizer, suggestion="This is due to minecraft's limitation")

        if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
            outer_key, inner_key = "clickEvent", "value"
        else:
            outer_key, inner_key = "click_event", "command"
        self.add_formatted_text_prop(
            outer_key, {
                "action": "run_command", inner_key: "/" + command[0]}, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProps.clickCommand",
    arg_type={
        "propertyName": ArgType.STRING,
        "indexString": ArgType.STRING,
        "function": ArgType.ARROW_FUNC,
        "local": ArgType.KEYWORD
    },
    name="text_props_click_command",
    defaults={
        "local": "false"
    },
    ignore={
        "function",
    }
)
class TextPropsClickCommand(JMCFunction):
    def call(self) -> str:
        command = self.datapack.parse_function_token(
            self.raw_args["function"].token,
            self.tokenizer, self.prefix)
        if not command:
            raise JMCValueError(
                "Unexpected empty arrow function",
                self.raw_args["function"].token,
                self.tokenizer)
        if len(command) > 1:
            raise JMCValueError(
                f"'{
                    self.call_string}' only allows 1 command (got {
                    len(command)})",
                self.raw_args["function"].token,
                self.tokenizer)
        if command[0].startswith("say"):
            raise JMCValueError(
                f"'{self.call_string}' doesn't allow 'say' command",
                self.raw_args["function"].token,
                self.tokenizer, suggestion="This is due to minecraft's limitation")

        if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
            outer_key, inner_key = "clickEvent", "value"
        else:
            outer_key, inner_key = "click_event", "command"

        @lru_cache()
        def inner(arg: str) -> SIMPLE_JSON_BODY:
            return {
                "action": "run_command", inner_key: "/" + command[0].replace(self.args["indexString"], arg)}
        self.add_formatted_text_prop(
            outer_key, inner, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProp.suggestCommand",
    arg_type={
        "propertyName": ArgType.STRING,
        "function": ArgType.ARROW_FUNC,
        "local": ArgType.KEYWORD
    },
    name="text_prop_suggest_command",
    defaults={
        "local": "false"
    },
    ignore={
        "function",
    }
)
class TextPropSuggestCommand(JMCFunction):
    def call(self) -> str:
        command = self.datapack.parse_function_token(
            self.raw_args["function"].token,
            self.tokenizer, self.prefix)
        if not command:
            raise JMCValueError(
                "Unexpected empty arrow function",
                self.raw_args["function"].token,
                self.tokenizer)
        if len(command) > 1:
            raise JMCValueError(
                f"'{
                    self.call_string}' only allows 1 command (got {
                    len(command)})",
                self.raw_args["function"].token,
                self.tokenizer)
        if command[0].startswith("say"):
            raise JMCValueError(
                f"'{self.call_string}' doesn't allow 'say' command",
                self.raw_args["function"].token,
                self.tokenizer, suggestion="This is due to minecraft's limitation")

        if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
            outer_key, inner_key = "clickEvent", "value"
        else:
            outer_key, inner_key = "click_event", "command"

        self.add_formatted_text_prop(
            outer_key, {
                "action": "suggest_command", inner_key: "/" + command[0]}, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProps.suggestCommand",
    arg_type={
        "propertyName": ArgType.STRING,
        "indexString": ArgType.STRING,
        "function": ArgType.ARROW_FUNC,
        "local": ArgType.KEYWORD
    },
    name="text_props_suggest_command",
    defaults={
        "local": "false"
    },
    ignore={
        "function",
    }
)
class TextPropsSuggestCommand(JMCFunction):
    def call(self) -> str:
        command = self.datapack.parse_function_token(
            self.raw_args["function"].token,
            self.tokenizer, self.prefix)
        if not command:
            raise JMCValueError(
                "Unexpected empty arrow function",
                self.raw_args["function"].token,
                self.tokenizer)
        if len(command) > 1:
            raise JMCValueError(
                f"'{
                    self.call_string}' only allows 1 command (got {
                    len(command)})",
                self.raw_args["function"].token,
                self.tokenizer)
        if command[0].startswith("say"):
            raise JMCValueError(
                f"'{self.call_string}' doesn't allow 'say' command",
                self.raw_args["function"].token,
                self.tokenizer, suggestion="This is due to minecraft's limitation")

        if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
            outer_key, inner_key = "clickEvent", "value"
        else:
            outer_key, inner_key = "click_event", "command"

        @lru_cache()
        def inner(arg: str) -> SIMPLE_JSON_BODY:
            return {
                "action": "suggest_command", inner_key: "/" + command[0].replace(self.args["indexString"], arg)}
        self.add_formatted_text_prop(
            outer_key, inner, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProp.clickURL",
    arg_type={
        "propertyName": ArgType.STRING,
        "url": ArgType.STRING,
        "local": ArgType.KEYWORD
    },
    name="text_prop_click_url",
    defaults={
        "local": "false"
    }
)
class TextPropClickURL(JMCFunction):
    def call(self) -> str:
        url = self.raw_args["url"]
        if not url:
            raise JMCValueError(
                "Unexpected empty URL",
                self.raw_args["url"].token,
                self.tokenizer)

        if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
            outer_key, inner_key = "clickEvent", "value"
        else:
            outer_key, inner_key = "click_event", "url"

        self.add_formatted_text_prop(
            outer_key, {
                "action": "open_url", inner_key: self.args["url"]}, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProps.clickURL",
    arg_type={
        "propertyName": ArgType.STRING,
        "indexString": ArgType.STRING,
        "url": ArgType.STRING,
        "local": ArgType.KEYWORD
    },
    name="text_props_click_url",
    defaults={
        "local": "false"
    }
)
class TextPropsClickURL(JMCFunction):
    def call(self) -> str:
        url = self.raw_args["url"]
        if not url:
            raise JMCValueError(
                "Unexpected empty URL",
                self.raw_args["url"].token,
                self.tokenizer)

        if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
            outer_key, inner_key = "clickEvent", "value"
        else:
            outer_key, inner_key = "click_event", "url"

        @lru_cache()
        def inner(arg: str) -> SIMPLE_JSON_BODY:
            return {
                "action": "open_url", inner_key: self.args["url"].replace(self.args["indexString"], arg)}
        self.add_formatted_text_prop(
            outer_key, inner, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProp.clickPage",
    arg_type={
        "propertyName": ArgType.STRING,
        "page": ArgType.INTEGER,
        "local": ArgType.KEYWORD
    },
    name="text_prop_click_page",
    defaults={
        "local": "false"
    },
    number_type={
        "page": NumberType.POSITIVE
    }
)
class TextPropClickPage(JMCFunction):
    def call(self) -> str:
        page = self.raw_args["page"]
        if not page:
            raise JMCValueError(
                "Unexpected empty page number",
                self.raw_args["page"].token,
                self.tokenizer)

        if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
            key = "clickEvent"
            body: dict[str, str | int] = {
                "action": "change_page", "value": self.args["page"]}
        else:
            key = "click_event"
            body = {
                "action": "change_page", "page": int(self.args["page"])}

        self.add_formatted_text_prop(key, body, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProps.clickPage",
    arg_type={
        "propertyName": ArgType.STRING,
        "local": ArgType.KEYWORD
    },
    name="text_props_click_page",
    defaults={
        "local": "false"
    }
)
class TextPropsClickPage(JMCFunction):
    def call(self) -> str:

        @lru_cache()
        def inner(arg: str) -> SIMPLE_JSON_BODY:
            if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
                return {"action": "change_page", "value": arg}
            else:
                return {"action": "change_page", "page": int(arg)}
        self.add_formatted_text_prop(
            "clickEvent" if self.datapack.version < PackVersionFeature.TEXT_COMPONENT else "click_event",
            inner, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProp.clipboard",
    arg_type={
        "propertyName": ArgType.STRING,
        "text": ArgType.STRING,
        "local": ArgType.KEYWORD
    },
    name="text_prop_clipboard",
    defaults={
        "local": "false"
    }
)
class TextPropClipboard(JMCFunction):
    def call(self) -> str:
        text = self.raw_args["text"]
        if not text:
            raise JMCValueError(
                "Unexpected empty clipboard content",
                self.raw_args["text"].token,
                self.tokenizer)

        self.add_formatted_text_prop(
            "clickEvent", {
                "action": "copy_to_clipboard", "value": self.args["text"]}, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProps.clipboard",
    arg_type={
        "propertyName": ArgType.STRING,
        "indexString": ArgType.STRING,
        "text": ArgType.STRING,
        "local": ArgType.KEYWORD
    },
    name="text_props_clipboard",
    defaults={
        "local": "false"
    }
)
class TextPropsClipboard(JMCFunction):
    def call(self) -> str:
        text = self.raw_args["text"]
        if not text:
            raise JMCValueError(
                "Unexpected emptyclipboard content",
                self.raw_args["text"].token,
                self.tokenizer)

        @lru_cache()
        def inner(arg: str) -> SIMPLE_JSON_BODY:
            return {
                "action": "copy_to_clipboard", "value": self.args["text"].replace(self.args["indexString"], arg)}
        self.add_formatted_text_prop(
            "clickEvent", inner, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProp.hoverText",
    arg_type={
        "propertyName": ArgType.STRING,
        "text": ArgType.STRING,
        "local": ArgType.KEYWORD
    },
    name="text_prop_hover_text",
    defaults={
        "local": "false"
    }
)
class TextPropHoverText(JMCFunction):
    def call(self) -> str:
        text = self.raw_args["text"]
        if not text:
            raise JMCValueError(
                "Unexpected empty FormattedText",
                self.raw_args["text"].token,
                self.tokenizer)

        text_to_show = json.loads(self.format_text("text"))

        if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
            outer_key, inner_key = "hoverEvent", "contents"
        elif self.datapack.version == PackVersionFeature.TEXT_COMPONENT:
            outer_key, inner_key = "hover_event", "text"
        else:
            outer_key, inner_key = "hover_event", "value"

        self.add_formatted_text_prop(
            outer_key, {
                "action": "show_text", inner_key: text_to_show}, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProps.hoverText",
    arg_type={
        "propertyName": ArgType.STRING,
        "indexString": ArgType.STRING,
        "text": ArgType.STRING,
        "local": ArgType.KEYWORD
    },
    name="text_props_hover_text",
    defaults={
        "local": "false"
    }
)
class TextPropsHoverText(JMCFunction):
    def call(self) -> str:
        text = self.raw_args["text"]
        if not text:
            raise JMCValueError(
                "Unexpected empty FormattedText",
                self.raw_args["text"].token,
                self.tokenizer)

        if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
            outer_key, inner_key = "hoverEvent", "contents"
        elif self.datapack.version == PackVersionFeature.TEXT_COMPONENT:
            outer_key, inner_key = "hover_event", "text"
        else:
            outer_key, inner_key = "hover_event", "value"

        @lru_cache()
        def inner(arg: str) -> SIMPLE_JSON_BODY:
            text_to_show = json.loads(
                self.format_text("text").replace(
                    self.args["indexString"], arg))
            return {"action": "show_text", inner_key: text_to_show}
        self.add_formatted_text_prop(
            outer_key, inner, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProp.hoverItem",
    arg_type={
        "propertyName": ArgType.STRING,
        "item": ArgType.JSON,
        "local": ArgType.KEYWORD
    },
    name="text_prop_hover_item",
    defaults={
        "local": "false"
    }
)
class TextPropHoverItem(JMCFunction):
    def call(self) -> str:
        item = self.raw_args["item"]
        if not item:
            raise JMCValueError(
                "Missing item in TextProp.hoverItem",
                self.raw_args["item"].token,
                self.tokenizer)

        item_to_show = json.loads(self.args["item"])

        if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
            key = "hoverEvent"
            body = {
                "action": "show_item",
                "contents": item_to_show
            }
        else:
            key = "hover_event"
            body = {
                "action": "show_item",
                **item_to_show
            }

        self.add_formatted_text_prop(key, body, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProps.hoverItem",
    arg_type={
        "propertyName": ArgType.STRING,
        "indexString": ArgType.STRING,
        "item": ArgType.JSON,
        "local": ArgType.KEYWORD
    },
    name="text_props_hover_item",
    defaults={
        "local": "false"
    }
)
class TextPropsHoverItem(JMCFunction):
    def call(self) -> str:
        item = self.raw_args["item"]
        if not item:
            raise JMCValueError(
                "Missing item in TextProps.hoverItem",
                self.raw_args["item"].token,
                self.tokenizer)

        @lru_cache()
        def inner(arg: str) -> SIMPLE_JSON_BODY:
            item_to_show = json.loads(
                self.args["item"].replace(
                    self.args["indexString"], arg))

            if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
                return {"action": "show_item", "contents": item_to_show}
            else:
                return {"action": "show_item", **item_to_show}

        self.add_formatted_text_prop(
            "hoverEvent" if self.datapack.version < PackVersionFeature.TEXT_COMPONENT else "hover_event",
            inner,
            self.check_bool("local")
        )
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProp.hoverEntity",
    arg_type={
        "propertyName": ArgType.STRING,
        "entity": ArgType.JSON,
        "local": ArgType.KEYWORD
    },
    name="text_prop_hover_entity",
    defaults={
        "local": "false"
    }
)
class TextPropHoverEntity(JMCFunction):
    def call(self) -> str:
        entity = self.raw_args["entity"]
        if not entity:
            raise JMCValueError(
                "Missing entity in TextProp.hoverEntity",
                self.raw_args["entity"].token,
                self.tokenizer)

        entity_to_show = json.loads(self.args["entity"])

        if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
            key = "hoverEvent"
            body = {
                "action": "show_entity",
                "contents": entity_to_show
            }
        else:
            key = "hover_event"
            body = {
                "action": "show_entity",
                **entity_to_show
            }

        self.add_formatted_text_prop(key, body, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProps.hoverEntity",
    arg_type={
        "propertyName": ArgType.STRING,
        "indexString": ArgType.STRING,
        "entity": ArgType.JSON,
        "local": ArgType.KEYWORD
    },
    name="text_props_hover_entity",
    defaults={
        "local": "false"
    }
)
class TextPropsHoverEntity(JMCFunction):
    def call(self) -> str:
        entity = self.raw_args["entity"]
        if not entity:
            raise JMCValueError(
                "Missing entity in TextProps.hoverEntity",
                self.raw_args["entity"].token,
                self.tokenizer)

        @lru_cache()
        def inner(arg: str) -> SIMPLE_JSON_BODY:
            entity_to_show = json.loads(
                self.args["entity"].replace(
                    self.args["indexString"], arg))

            if self.datapack.version < PackVersionFeature.TEXT_COMPONENT:
                return {"action": "show_entity", "contents": entity_to_show}
            else:
                return {"action": "show_entity", **entity_to_show}

        self.add_formatted_text_prop(
            "hoverEvent" if self.datapack.version < PackVersionFeature.TEXT_COMPONENT else "hover_event",
            inner,
            self.check_bool("local")
        )
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProp.font",
    arg_type={
        "propertyName": ArgType.STRING,
        "font": ArgType.STRING,
        "local": ArgType.KEYWORD
    },
    name="text_prop_font",
    defaults={
        "local": "false"
    }
)
class TextPropFont(JMCFunction):
    def call(self) -> str:
        font = self.raw_args["font"]
        if not font:
            raise JMCValueError(
                "Missing font in TextProp.font",
                self.raw_args["font"].token,
                self.tokenizer)

        self.add_formatted_text_prop(
            "font", self.args["font"], self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProps.font",
    arg_type={
        "propertyName": ArgType.STRING,
        "indexString": ArgType.STRING,
        "font": ArgType.STRING,
        "local": ArgType.KEYWORD
    },
    name="text_props_font",
    defaults={
        "local": "false"
    }
)
class TextPropsFont(JMCFunction):
    def call(self) -> str:
        font = self.raw_args["font"]
        if not font:
            raise JMCValueError(
                "Missing font in TextProps.font",
                self.raw_args["font"].token,
                self.tokenizer)

        @lru_cache()
        def inner(arg: str) -> SIMPLE_JSON_BODY:
            return self.args["font"].replace(self.args["indexString"], arg)
        self.add_formatted_text_prop(
            "font", inner, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProp.keybind",
    arg_type={
        "propertyName": ArgType.STRING,
        "keybind": ArgType.STRING,
        "local": ArgType.KEYWORD
    },
    name="text_prop_keybind",
    defaults={
        "local": "false"
    }
)
class TextPropKeybind(JMCFunction):
    def call(self) -> str:
        keybind = self.raw_args["keybind"]
        if not keybind:
            raise JMCValueError(
                "Missing keybind in TextProp.keybind",
                self.raw_args["keybind"].token,
                self.tokenizer)

        self.add_formatted_text_prop(
            "keybind", self.args["keybind"], self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProps.keybind",
    arg_type={
        "propertyName": ArgType.STRING,
        "indexString": ArgType.STRING,
        "keybind": ArgType.STRING,
        "local": ArgType.KEYWORD
    },
    name="text_props_keybind",
    defaults={
        "local": "false"
    }
)
class TextPropsKeybind(JMCFunction):
    def call(self) -> str:
        keybind = self.raw_args["keybind"]
        if not keybind:
            raise JMCValueError(
                "Missing keybind in TextProps.keybind",
                self.raw_args["keybind"].token,
                self.tokenizer)

        @lru_cache()
        def inner(arg: str) -> SIMPLE_JSON_BODY:
            return self.args["keybind"].replace(self.args["indexString"], arg)
        self.add_formatted_text_prop(
            "keybind", inner, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProp.nbt",
    arg_type={
        "propertyName": ArgType.STRING,
        "type": ArgType.KEYWORD,
        "source": ArgType.STRING,
        "path": ArgType.KEYWORD,
        "separator": ArgType.STRING,
        "interpret": ArgType.KEYWORD,
        "local": ArgType.KEYWORD
    },
    name="text_prop_nbt",
    defaults={
        "separator": ", ",
        "interpret": "false",
        "local": "false"
    }
)
class TextPropNBT(JMCFunction):
    def call(self) -> str:
        _type = self.raw_args["type"]
        if not _type:
            raise JMCValueError(
                "Missing NBT type in TextProp.nbt (should be `block`, `entity`, or `storage`)",
                self.raw_args["type"].token,
                self.tokenizer)
        source = self.raw_args["source"]
        if not source:
            raise JMCValueError(
                "Missing NBT source in TextProp.nbt",
                self.raw_args["source"].token,
                self.tokenizer)
        path = self.raw_args["path"]
        if not path:
            raise JMCValueError(
                "Missing NBT path in TextProp.nbt",
                self.raw_args["path"].token,
                self.tokenizer)

        output: SIMPLE_JSON_BODY = {
            self.args["type"]: self.args["source"],
            "nbt": self.args["path"],
            "interpret": self.args["interpret"]}
        if self.args["separator"] != ", ":
            output["separator"] = json.loads(  # type: ignore # fmt: off
                self.format_text("separator"))
        self.add_formatted_text_prop(
            "__private_nbt_expand__", output, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="TextProps.nbt",
    arg_type={
        "propertyName": ArgType.STRING,
        "indexString": ArgType.STRING,
        "type": ArgType.KEYWORD,
        "source": ArgType.STRING,
        "path": ArgType.KEYWORD,
        "separator": ArgType.STRING,
        "interpret": ArgType.KEYWORD,
        "local": ArgType.KEYWORD
    },
    name="text_props_nbt",
    defaults={
        "separator": ", ",
        "interpret": "false",
        "local": "false"
    }
)
class TextPropsNBT(JMCFunction):
    def call(self) -> str:
        _type = self.raw_args["type"]
        if not _type:
            raise JMCValueError(
                "Missing NBT type in TextProp.nbt (should be `block`, `entity`, or `storage`)",
                self.raw_args["type"].token,
                self.tokenizer)
        source = self.raw_args["source"]
        if not source:
            raise JMCValueError(
                "Missing NBT source in TextProp.nbt",
                self.raw_args["source"].token,
                self.tokenizer)
        path = self.raw_args["path"]
        if not path:
            raise JMCValueError(
                "Missing NBT path in TextProp.nbt",
                self.raw_args["path"].token,
                self.tokenizer)

        @lru_cache()
        def inner(arg: str) -> SIMPLE_JSON_BODY:
            output: SIMPLE_JSON_BODY = {self.args["type"]: self.args["source"].replace(
                self.args["indexString"], arg), "nbt": self.args["path"].replace(
                self.args["indexString"], arg), "interpret": self.args["interpret"]}
            if self.args["separator"] != ", ":
                output["separator"] = self.format_text(  # type: ignore # fmt: off
                    "separator")
            return output
        self.add_formatted_text_prop(
            "__private_nbt_expand__", inner, self.check_bool("local"))
        return ""


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Debug.watch",
    arg_type={
        "variable": ArgType.SCOREBOARD,
        "src": ArgType.KEYWORD
    },
    defaults={
        "src": "true"
    },
    name="debug_watch"
)
class DebugWatch(JMCFunction):
    function_group_name = "__debug_watch__"
    tmp = "__debug__.tmp"

    def call(self) -> str:
        is_src = self.check_bool("src")
        if self.datapack.data.is_too_late_debug_watch:
            raise JMCSyntaxException(f"At least 1 variable operation was performed before calling {self.call_string}", self.self_token, self.tokenizer)
        objective, player = self.args["variable"].split()
        if (objective, player) in self.datapack.data.watching:
            raise JMCSyntaxException(f"{objective}:{player} is already being watched.", self.raw_args["variable"].token, self.tokenizer)
        self.datapack.data.watching[(objective, player)] = is_src
        return ""

    @classmethod
    def variable_operation_wrapper(cls, return_command: str, player: str, objective: str, datapack: "DataPack") -> str:
        if (player, objective) not in datapack.data.watching:
            return return_command

        assert datapack.data.last_code_data is not None
        tellraw = 'tellraw @a ["",{"text":"[JMC] ","color":"gold","bold":true}'
        if objective != datapack.var_name:
            tellraw += f',{{"text":"{objective}","color":"red"}},{{"text":":","color":"aqua"}}'
        tellraw += f',{{"text":"{player} ","color":"gold"}}'
        tellraw += ',{"text":"| ","color":"aqua","bold":true}'
        tellraw += f',{{"score":{{"name":"{cls.tmp}","objective":"{datapack.var_name}"}}}}'
        tellraw += ',{"text":" -> ","color":"aqua","bold":true}'
        tellraw += f',{{"score":{{"name":"{player}","objective":"{objective}"}}}}'
        if player.startswith("@"):
            tellraw += ',{"text":" | ","color":"aqua","bold":true}'
            tellraw += f',{{"selector":"{player}"}}'
        if datapack.data.watching[(player, objective)]:
            tellraw += ',{"text":" | ","color":"aqua","bold":true}'
            tellraw += f',{{"text":"{datapack.data.last_code_data[0]}","color":"yellow"}}'
            tellraw += ',{"text":" | ","color":"aqua","bold":true}'
            tellraw += f',{{"text":"{datapack.data.last_code_data[1]}","color":"yellow"}}'
        tellraw += ']'
        return datapack.add_raw_private_function(cls.function_group_name, [
            f"scoreboard players operation {cls.tmp} {datapack.var_name} = {player} {objective}",
            return_command,
            f'execute unless score {player} {objective} = {cls.tmp} {datapack.var_name} run ' + tellraw
        ])


@func_property(
    func_type=FuncType.LOAD_ONLY,
    call_string="Debug.history",
    arg_type={
        "variable": ArgType.SCOREBOARD,
        "cache": ArgType.INTEGER
    },
    defaults={
        "cache": "5"
    },
    number_type={
        "cache": NumberType.POSITIVE
    },
    name="debug_history"
)
class DebugHistory(JMCFunction):
    scoreboard_name = "debug_history"
    current = "__debug__.current"
    tmp = "__debug__.tmp"

    def call(self) -> str:
        if not self.is_never_used():
            raise Exception("add error here")
        cache = int(self.args["cache"])
        if not self.is_never_used():
            raise Exception("add error here")

        score, obj = self.args["variable"].split()
        self.datapack.add_objective(self.scoreboard_name)
        self.datapack.add_load_command(f'scoreboard objectives modify {self.scoreboard_name} displayname {{"text":"History of {obj}:{score}","color":"gold","bold":true}}')
        record_call = self.datapack.add_raw_private_function(self.name, [
            *(f"scoreboard players operation [{i + 1}] {self.scoreboard_name} = [{i}] {self.scoreboard_name}"
                for i in range(cache - 1, 0, -1)),
            f"scoreboard players operation [1] {self.scoreboard_name} = [CURRENT] {self.scoreboard_name}",
            f"scoreboard players operation [CURRENT] {self.scoreboard_name} = {self.current} {self.datapack.var_name}",
        ], "record")
        self.datapack.add_tick_command(self.datapack.add_raw_private_function(self.name, [
            f"scoreboard players operation {self.current} {self.datapack.var_name} = {self.args["variable"]}",
            f"execute unless score {self.current} {self.datapack.var_name} = {self.tmp} {self.datapack.var_name} run {record_call}",
            f"scoreboard players operation {self.tmp} {self.datapack.var_name} = {self.current} {self.datapack.var_name}"
        ], "main"))
        return ""
