import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Привет! Я бот для конвертации темпа бега и скорости.
    
Отправь мне:
- Темп бега в формате *мм:сс* (например, 5:20), и я скажу скорость в км/ч
- Скорость в км/ч (например, 12.5), и я скажу темп бега

Поддерживаются оба формата!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# Конвертация темпа в скорость
def pace_to_speed(pace_str: str) -> float:
    try:
        minutes, seconds = map(int, pace_str.split(':'))
        total_minutes = minutes + seconds / 60
        speed = 60 / total_minutes
        return round(speed, 2)
    except:
        return None

# Конвертация скорости в темп
def speed_to_pace(speed: float) -> str:
    try:
        total_seconds_per_km = 3600 / speed
        minutes = int(total_seconds_per_km // 60)
        seconds = int(total_seconds_per_km % 60)
        return f"{minutes}:{seconds:02d}"
    except:
        return None

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Проверяем, является ли ввод темпом (содержит :)
    if ':' in text:
        result = pace_to_speed(text)
        if result is not None:
            response = f"Темп *{text}* мин/км = *{result}* км/ч"
        else:
            response = "Неверный формат темпа. Используйте мм:сс (например, 5:20)"
    else:
        # Пробуем обработать как скорость
        try:
            speed = float(text.replace(',', '.'))
            result = speed_to_pace(speed)
            if result is not None:
                response = f"Скорость *{speed}* км/ч = темп *{result}* мин/км"
            else:
                response = "Неверное значение скорости"
        except ValueError:
            response = "Неверный формат. Отправьте темп (мм:сс) или скорость (число)"
    
    await update.message.reply_text(response, parse_mode='Markdown')

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка при обработке сообщения: {context.error}")
    if update.message:
        await update.message.reply_text("Произошла ошибка при обработке вашего запроса")

def main():
    # Создаем приложение и передаем токен бота
    application = Application.builder().token("8031841222:AAFBzcejfbS7E2lMPaDLjwP_sz1tUVmE1Ww").build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
