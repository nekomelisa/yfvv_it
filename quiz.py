import json
import random
from pathlib import Path


TESTS_DIR = Path("tests")

TOPICS = {
    "01": "Алгоритми та обчислювальна складність",
    "02": "Архітектура компʼютера",
    "03": "Бази та сховища даних",
    "04": "Інженерія систем і програмного забезпечення",
    "05": "Кібербезпека та захист інформації",
    "06": "Прикладна математика",
    "07": "Компʼютерні мережі та обмін даними",
    "08": "Операційні системи",
    "09": "Основи мов програмування",
    "10": "Штучний інтелект",
}


def load_questions_from_file(file_path: Path, topic_id: str) -> list[dict]:
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не знайдено: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        questions = json.load(file)

    for index, question in enumerate(questions, start=1):
        question["topic_id"] = topic_id
        question["topic_name"] = TOPICS.get(topic_id, f"Тема {topic_id}")
        question["source_number"] = index

    return questions


def get_available_files() -> list[str]:
    if not TESTS_DIR.exists():
        raise FileNotFoundError(
            f"Папку {TESTS_DIR} не знайдено. Створи папку tests і поклади туди json-файли."
        )

    files = sorted(TESTS_DIR.glob("*.json"))
    return [file.stem for file in files]


def choose_mode() -> list[str]:
    available = get_available_files()

    print("\nДоступні файли:")
    for topic_id in available:
        topic_name = TOPICS.get(topic_id, "Невідома тема")
        print(f"{topic_id}. {topic_name}")

    print("\nВведи номер файлу, наприклад: 01")
    print("Або введи: all")
    print("all = симуляція реального тесту з усіх доступних файлів")

    while True:
        choice = input("\nЗвідки беремо питання? ").strip().lower()

        if choice == "all":
            return available

        if choice in available:
            return [choice]

        print("Немає такого файлу. Так, машина перемогла на етапі вибору файлу. Спробуй ще раз.")


def choose_question_count(total_available: int) -> int:
    print(f"\nДоступно питань: {total_available}")
    print("Введи кількість питань або all")

    while True:
        choice = input("Скільки питань беремо? ").strip().lower()

        if choice == "all":
            return total_available

        if choice.isdigit():
            number = int(choice)

            if 1 <= number <= total_available:
                return number

            print(f"Введи число від 1 до {total_available}. Математика, на жаль, усе ще існує.")
        else:
            print("Треба число або all. Не творче есе, а налаштування тесту.")


def choose_show_answers_immediately() -> bool:
    print("\nПоказувати правильну відповідь одразу після кожного питання?")
    print("y = так")
    print("n = ні")

    while True:
        choice = input("Твій вибір: ").strip().lower()

        if choice in ["y", "yes", "так", "т"]:
            return True

        if choice in ["n", "no", "ні", "н"]:
            return False

        print("Введи y або n. Так, демократія має обмеження.")


def normalize_answer(answer: str) -> str:
    return answer.strip().upper()


def ask_question(question: dict, question_number: int, total: int, show_answer_immediately: bool) -> dict | None:
    print("\n" + "=" * 70)
    print(f"Питання {question_number}/{total}")
    print(f"Тема {question['topic_id']}: {question['topic_name']}")
    print(f"Номер у файлі: {question['source_number']}")
    print("-" * 70)
    print(question["question"])
    print()

    options = list(question["options"].items())
    random.shuffle(options)

    for letter, text in options:
        print(f"{letter}. {text}")

    valid_answers = {letter for letter, _ in options}

    while True:
        raw_answer = input("\nТвоя відповідь: ").strip()

        if raw_answer.lower() in ["stop", "стоп"]:
            return None

        user_answer = normalize_answer(raw_answer)

        if user_answer in valid_answers:
            break

        print(
            f"Введи одну з літер: {', '.join(sorted(valid_answers))} "
            "або stop/стоп для завершення тесту. Не ієрогліфи, не настрій, літеру."
        )

    correct_answer = normalize_answer(question["answer"])
    is_correct = user_answer == correct_answer

    if show_answer_immediately:
        if is_correct:
            print("\nПравильно.")
        else:
            print(f"\nНеправильно. Правильна відповідь: {correct_answer}")

        print(f"Пояснення: {question['explanation']}")

    return {
        "question_number": question_number,
        "topic_id": question["topic_id"],
        "topic_name": question["topic_name"],
        "source_number": question["source_number"],
        "question": question["question"],
        "options": question["options"],
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct,
        "explanation": question["explanation"],
    }


def print_final_report(results: list[dict]) -> None:
    correct_count = sum(1 for item in results if item["is_correct"])
    total = len(results)
    percent = correct_count / total * 100 if total else 0

    print("\n" + "#" * 70)
    print("РЕЗУЛЬТАТ")
    print("#" * 70)
    print(f"Загальний бал: {correct_count}/{total}")
    print(f"Відсоток: {percent:.1f}%")

    print("\n" + "#" * 70)
    print("РОЗБІР ПИТАНЬ")
    print("#" * 70)

    for item in results:
        status = "✓" if item["is_correct"] else "✗"

        print("\n" + "=" * 70)
        print(f"{status} Питання {item['question_number']}")
        print(f"Тема {item['topic_id']}: {item['topic_name']}")
        print(f"Номер у файлі: {item['source_number']}")
        print("-" * 70)
        print(item["question"])
        print()

        for letter, text in item["options"].items():
            marker = ""

            if letter == item["correct_answer"]:
                marker = " ← правильна"

            if letter == item["user_answer"]:
                marker += " ← твоя відповідь"

            print(f"{letter}. {text}{marker}")

        print()
        print(f"Твоя відповідь: {item['user_answer']}")
        print(f"Правильна відповідь: {item['correct_answer']}")
        print(f"Пояснення: {item['explanation']}")


def main() -> None:
    print("Консольний тренажер тестів")
    print("Бо страждання має бути автоматизоване.")

    selected_files = choose_mode()

    all_questions = []

    for topic_id in selected_files:
        file_path = TESTS_DIR / f"{topic_id}.json"
        questions = load_questions_from_file(file_path, topic_id)
        all_questions.extend(questions)

    if not all_questions:
        print("Питань немає. Це або дзен, або помилка у файлах.")
        return

    random.shuffle(all_questions)

    question_count = choose_question_count(len(all_questions))
    selected_questions = random.sample(all_questions, question_count)

    if len(selected_files) > 1:
        random.shuffle(selected_questions)

    show_answer_immediately = choose_show_answers_immediately()

    print("\nПід час тесту можна ввести stop або стоп, щоб завершити тест достроково.")

    results = []

    for index, question in enumerate(selected_questions, start=1):
        result = ask_question(
            question=question,
            question_number=index,
            total=question_count,
            show_answer_immediately=show_answer_immediately,
        )

        if result is None:
            print("\nТест завершено достроково.")
            break

        results.append(result)

    if results:
        print_final_report(results)
    else:
        print("\nТест завершено без жодної відповіді. Абсолютний мінімалізм, майже мистецтво.")


if __name__ == "__main__":
    main()