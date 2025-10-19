from openai import OpenAI


class OpenRouterAI:
    def __init__(self, api_keys, site_url="https://github.com", site_name="MatshLibrary"):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.site_url = site_url
        self.site_name = site_name
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Инициализирует клиент с текущим API ключом"""
        if self.api_keys:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_keys[self.current_key_index],
            )

    def _rotate_key(self):
        """Переключает на следующий API ключ"""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        print(f"🔄 Переключение на API ключ #{self.current_key_index + 1}")
        self._initialize_client()

    def ask(self, question, max_retries=3):
        """Задать вопрос нейросети с автоматической ротацией ключей"""
        for attempt in range(max_retries):
            try:
                if not self.client:
                    raise Exception("Клиент не инициализирован")

                completion = self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": self.site_url,
                        "X-Title": self.site_name,
                    },
                    extra_body={},
                    model="tngtech/deepseek-r1t2-chimera:free",  # Модель фиксированная
                    messages=[
                        {
                            "role": "user",
                            "content": question
                        }
                    ],
                    timeout=30
                )
                return completion.choices[0].message.content

            except Exception as e:
                error_msg = str(e).lower()
                print(f"❌ Попытка {attempt + 1} не удалась: {e}")

                # Проверяем, является ли ошибка связанной с API ключом
                if any(keyword in error_msg for keyword in ['key', 'auth', '401', '403', 'invalid', 'quota']):
                    if len(self.api_keys) > 1:
                        self._rotate_key()
                        continue

                if attempt == max_retries - 1:
                    return f"Ошибка после {max_retries} попыток: {e}"

        return "Неизвестная ошибка"


# Пул API ключей
API_KEYS_POOL_1 = [
    "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",
    "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",
]

API_KEYS_POOL_2 = [
    "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",
    "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",
]

# Создаем экземпляры
ai1 = OpenRouterAI(API_KEYS_POOL_1)
ai2 = OpenRouterAI(API_KEYS_POOL_2)


def depsek1(question):
    """
    Задать вопрос нейросети используя первый пул API ключей

    Args:
        question (str): Текст вопроса для нейросети

    Returns:
        str: Ответ от нейросети или сообщение об ошибке
    """
    return ai1.ask(question)


def depsek2(question):
    """
    Задать вопрос нейросети используя второй пул API ключей

    Args:
        question (str): Текст вопроса для нейросети

    Returns:
        str: Ответ от нейросети или сообщение об ошибке
    """
    return ai2.ask(question)


def add_api_key_to_pool1(api_key):
    """Добавить новый API ключ в первый пул"""
    API_KEYS_POOL_1.append(api_key)
    ai1.api_keys = API_KEYS_POOL_1
    print(f"✅ Добавлен новый ключ в пул 1. Всего ключей: {len(API_KEYS_POOL_1)}")


def add_api_key_to_pool2(api_key):
    """Добавить новый API ключ во второй пул"""
    API_KEYS_POOL_2.append(api_key)
    ai2.api_keys = API_KEYS_POOL_2
    print(f"✅ Добавлен новый ключ в пул 2. Всего ключей: {len(API_KEYS_POOL_2)}")


def get_pool_stats():
    """Получить статистику по пулам ключей"""
    return {
        "pool1_keys_count": len(API_KEYS_POOL_1),
        "pool2_keys_count": len(API_KEYS_POOL_2),
        "pool1_current_index": ai1.current_key_index,
        "pool2_current_index": ai2.current_key_index
    }