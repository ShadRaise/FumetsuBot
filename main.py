import discord
from discord.ext import tasks
import datetime
import asyncio
import os  # 追加

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

CHANNEL_ID = 1350971940244033647  # 「不滅」フォーラムチャンネルのID
THREAD_NAME = "本日の参加可否"

@tasks.loop(minutes=1)  # 1分ごとに実行
async def daily_game_check():
    try:
        now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
        target_time = now.replace(hour=12, minute=0, second=0, microsecond=0)  # 12:00 JST
        print(f"daily_game_check: 現在時刻: {now}, 目標時刻: {target_time}")  # ログ追加

        # 今日すでに投稿済みかチェック
        today_str = now.strftime('%Y-%m-%d')
        channel = client.get_channel(CHANNEL_ID)
        print(f"daily_game_check: チャンネル取得結果: {channel}, タイプ: {type(channel)}")  # ログ追加
        if channel and isinstance(channel, discord.ForumChannel):
            print(f"daily_game_check: フォーラムチャンネルが見つかりました: {channel.name}")  # ログ追加
            thread = None
            print("daily_game_check: スレッド検索を開始します")  # ログ追加
            for t in channel.threads:
                print(f"daily_game_check: スレッド確認: {t.name}")  # ログ追加
                if t.name == THREAD_NAME:
                    thread = t
                    break
            if thread:
                print(f"daily_game_check: 既存のスレッドが見つかりました: {thread.name}")  # ログ追加
                # スレッド内の最新メッセージを確認
                async for message in thread.history(limit=1):
                    if message.content.startswith(f"【{today_str}】"):
                        print(f"daily_game_check: 今日 ({today_str}) はすでに投稿済みです")  # ログ追加
                        return  # 今日すでに投稿済みなので終了
            if now >= target_time and now.date() == target_time.date():
                print("daily_game_check: 投稿条件を満たしました")  # ログ追加
                if thread:
                    print(f"daily_game_check: 既存のスレッドにメッセージを追加します")  # ログ追加
                    message = await thread.send(f"【{now.strftime('%Y-%m-%d')}】本日の参加可否")
                    print(f"daily_game_check: メッセージを送信しました: {message.content}")  # ログ追加
                    # リアクションを追加
                    reactions = ["🆗", "🆖", "❔", "🕗", "🕘", "🕙", "🕚", "🕛"]
                    for reaction in reactions:
                        try:
                            await message.add_reaction(reaction)
                            print(f"daily_game_check: リアクションを追加しました: {reaction}")  # ログ追加
                        except Exception as e:
                            print(f"daily_game_check: リアクション追加エラー: {reaction}, エラー: {e}")  # ログ追加
                else:
                    print(f"daily_game_check: スレッド '{THREAD_NAME}' が見つかりませんでした")  # ログ追加
                    # 新しいスレッドを作成
                    thread = await channel.create_thread(
                        name=THREAD_NAME,
                        content=f"参加したい方はスレッドにメッセージを送信してください！({now.strftime('%Y-%m-%d')}) スレッドが自動的に作成されました。",
                        auto_archive_duration=1440,
                        reason="自動投稿"
                    )
                    print(f"daily_game_check: 新しいスレッドを作成しました: {thread.name}")  # ログ追加
            else:
                print("daily_game_check: 投稿条件を満たしていません（目標時刻前または日付が異なる）")  # ログ追加
        else:
            print("daily_game_check: チャンネルが見つからないか、フォーラムチャンネルではありません")  # ログ追加
    except Exception as e:
        print(f"daily_game_check: タスク実行中にエラーが発生しました: {e}")  # ログ追加

@client.event
async def on_ready():
    print(f'ログインしました: {client.user}')
    if not daily_game_check.is_running():
        print("タスクを開始します")
        daily_game_check.start()

# 再接続を試みるループ
async def main():
    while True:
        try:
            await client.start(os.getenv('DISCORD_TOKEN'))  # 環境変数を使用
        except Exception as e:
            print(f"接続エラー: {e}")
            print("5秒後に再接続を試みます...")
            await asyncio.sleep(5)

# イベントループを実行
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())