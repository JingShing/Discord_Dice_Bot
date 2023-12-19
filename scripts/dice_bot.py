# roll ndm
# roll ndm(+-*/)a
# roll ndm(=<><=>=)a
# sc a n/qde，成功時輸出 a-n，失敗時輸出 a-qde
# sc a ndm/qde，成功時輸出 a-ndm，失敗時輸出 a-qde
# sc a ldr/n，成功時輸出 a-ldr，失敗時輸出 a-n
# sc a n/m，成功時輸出 a-n，失敗時輸出 a-m
# skill n skill_name
# 創角
import discord
import random
import re
import operator

TOKEN = "discord_bot_token"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

operators = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
        
    # dice functions
    if "創角" == message.content:
        character_info = ""
        stats = ["STR","DEX","CON","POW","APP","SIZ","INT","EDU","LUK"]
        for i in stats:
            results = roll_dice(3,6)
            character_info+=(i+f'：({"+".join(map(str, results))})\*5={sum(results)*5}\n')
        await message.reply(character_info)

    if "roll" in message.content or "skill" in message.content or "sc" in message.content:
        match_roll = re.match(r'^roll (\d+)d(\d+)$', message.content)    
        match_calc = re.match(r'^roll (\d+)d(\d+)([+\-*/])(\d+)$', message.content)
        match_conditional = re.match(r'^roll (\d+)d(\d+)([><=]+)(\d+)$', message.content)
        # match_skill = re.match(r'^skill (\d+) (.+)$', message.content)
        # match_sc = re.match(r'^sc (\d+) ([^/]+)\/(.+)$', message.content)
        match_skill = message.content.split(" ")[0] == "skill"
        match_sc = message.content.split(" ")[0] == "sc"

        if match_roll:
            num_dice = int(match_roll.group(1))
            dice_faces = int(match_roll.group(2))

            if num_dice <= 0 or dice_faces <= 0:
                await message.channel.send('請輸入有效數字')
                return

            results = [random.randint(1, dice_faces) for _ in range(num_dice)]
            number = sum(results)
            all_dice_result = "省略"
            if num_dice <= 30:
                all_dice_result = ", ".join(map(str, results))
            await message.reply(f'骰出了 {num_dice} 個 {dice_faces} 面骰，結果： {all_dice_result}，總和{number}')

        elif match_calc:
            num_dice = int(match_calc.group(1))
            dice_faces = int(match_calc.group(2))
            operand = match_calc.group(3)
            modifier = int(match_calc.group(4))

            if num_dice <= 0 or dice_faces <= 0:
                await message.channel.send('請輸入有效數字')
                return

            results = [random.randint(1, dice_faces) for _ in range(num_dice)]
            result_sum = sum(results)
            all_dice_result = "省略"
            if num_dice <= 30:
                all_dice_result = ", ".join(map(str, results))
            if operand == "/" and modifier == 0:
                await message.reply("不要除零啦！")
            else:
                calculated_result = operators[operand](result_sum, modifier)
                await message.reply(f'骰出了 {num_dice} 個 {dice_faces} 面骰，結果： {all_dice_result}，總和{result_sum}，計算結果{calculated_result}')

        elif match_conditional:
            num_dice = int(match_conditional.group(1))
            dice_faces = int(match_conditional.group(2))
            operand = match_conditional.group(3)
            compare_value = int(match_conditional.group(4))

            if num_dice <= 0 or dice_faces <= 0:
                await message.channel.send('請輸入有效數字')
                return

            results = [random.randint(1, dice_faces) for _ in range(num_dice)]
            result_sum = sum(results)
            detect_operand = False

            if operand == '>':
                if result_sum > compare_value:
                    detect_operand = True
                else:
                    detect_operand = False
            elif operand == '<':
                if result_sum < compare_value:
                    detect_operand = True
                else:
                    detect_operand = False
            if operand == '>=':
                if result_sum >= compare_value:
                    detect_operand = True
                else:
                    detect_operand = False
            elif operand == '<=':
                if result_sum <= compare_value:
                    detect_operand = True
                else:
                    detect_operand = False
            elif operand == '=':
                if result_sum == compare_value:
                    detect_operand = True
                else:
                    detect_operand = False

            all_dice_result = "省略"
            if num_dice <= 30:
                all_dice_result = ", ".join(map(str, results))
            if detect_operand:
                await message.reply(f'骰出了 {num_dice} 個 {dice_faces} 面骰，結果： {all_dice_result}，總和{result_sum}，判定成功')
            else:
                await message.reply(f'骰出了 {num_dice} 個 {dice_faces} 面骰，結果： {all_dice_result}，總和{result_sum}，判定失敗')

        elif match_skill:
            words = message.content.split(" ")
            roll_value = int(words[1])
            skill_name = "沒有技能名稱"
            if len(words)>2:
                skill_name = words[2]
            dice_result = random.randint(1, 100)

            if dice_result <= roll_value:
                if dice_result <= 5:
                    await message.reply(f'## {skill_name} 大成功！({dice_result}<={roll_value})')
                elif dice_result <= roll_value/5:
                    await message.reply(f'{skill_name} 極限成功！({dice_result}<={roll_value})')
                elif dice_result <= roll_value/2:
                    await message.reply(f'{skill_name} 困難成功！({dice_result}<={roll_value})')
                else:
                    await message.reply(f'{skill_name} 普通成功！({dice_result}<={roll_value})')
            else:
                if dice_result > 95:
                    await message.reply(f'## {skill_name} 大失敗！({dice_result}<={roll_value})')
                else:
                    await message.reply(f'{skill_name} 普通失敗！({dice_result}<={roll_value})')

        elif match_sc:
            # sc san_value p1/p2
            words = message.content.split(" ")
            roll_value = int(words[1])
            dice_result = random.randint(1, 100)
            if "/" in words[2]:
                penalty = words[2].split("/")
                if len(penalty) != 2:
                    await message.reply("san 懲罰填寫錯誤。")
            else:
                await message.reply("san 懲罰填寫錯誤。")
            
            all_fail = False
            if dice_result>=95:
                all_fail = True

            p1 = penalty[0]
            p2 = penalty[1]
            p1 = penalty_calculate(p1)
            p2 = penalty_calculate(p2, all_fail)
            if dice_result <= roll_value:
                await message.reply(f'(骰值{dice_result}<=SAN{roll_value})：成功！：扣{p1}，剩餘{roll_value-p1}')
            else:
                if all_fail:
                    await message.reply(f'## (骰值{dice_result}>SAN{roll_value})：大失敗！：扣{p2}，剩餘{roll_value-p2}')
                else:
                    await message.reply(f'(骰值{dice_result}>SAN{roll_value})：失敗！：扣{p2}，剩餘{roll_value-p2}')

def digit_count(number:int)->int:
    return len(str(number))

def format_to_e(number:int):
    return format(number, "e")

def penalty_calculate(p:str, all_fail = False)->int:
    if "d" in p:
        dice_faces = int(p.split("d")[-1])
        num_dice = int(p.split("d")[0])
        if all_fail:
            p = dice_faces*num_dice
        else:
            p = sum([random.randint(1, dice_faces) for _ in range(num_dice)])
    else:
        p = int(p)
    return p

def roll_dice(num_dice, dice_faces, need_sum=False):
    if need_sum:
        return sum([random.randint(1, dice_faces) for _ in range(num_dice)])
    return [random.randint(1, dice_faces) for _ in range(num_dice)]

client.run(TOKEN)
