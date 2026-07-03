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


def choose_quiz_mode() -> str:
    print("\nОбери режим проходження:")
    print("test  = не показувати правильні відповіді одразу, повний розбір у кінці")
    print("check = показувати правильні відповіді одразу, повний розбір у кінці")
    print("study = показувати правильні відповіді одразу і повторювати помилки до правильної відповіді")

    while True:
        choice = input("Твій вибір: ").strip().lower()

        if choice in ["test", "t", "тест"]:
            return "test"

        if choice in ["check", "c", "перевірка", "п"]:
            return "check"

        if choice in ["study", "s", "навчання", "н"]:
            return "study"

        print("Введи test, check або study. Так, режимів аж три, людство ризикнуло.")


def normalize_answer(answer: str) -> str:
    return answer.strip().upper()


def shuffle_options(question: dict) -> tuple[dict[str, str], str]:
    original_options = question["options"]
    original_correct_letter = normalize_answer(question["answer"])
    correct_text = original_options[original_correct_letter]

    option_texts = list(original_options.values())
    random.shuffle(option_texts)

    new_letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
    shuffled_options = {}

    for letter, text in zip(new_letters, option_texts):
        shuffled_options[letter] = text

    new_correct_letter = None

    for letter, text in shuffled_options.items():
        if text == correct_text:
            new_correct_letter = letter
            break

    if new_correct_letter is None:
        raise ValueError("Не вдалося знайти правильну відповідь після перемішування. Вражаюче, але погано.")

    return shuffled_options, new_correct_letter


def ask_question(
    question: dict,
    question_number: int,
    total: int,
    show_answer_immediately: bool,
) -> dict | None:
    print("\n" + "=" * 70)
    print(f"Питання {question_number}/{total}")
    print(f"Тема {question['topic_id']}: {question['topic_name']}")
    print(f"Номер у файлі: {question['source_number']}")
    print("-" * 70)
    print(question["question"])
    print()

    shuffled_options, correct_answer = shuffle_options(question)

    for letter in sorted(shuffled_options):
        print(f"{letter}. {shuffled_options[letter]}")

    valid_answers = set(shuffled_options.keys())

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
        "options": shuffled_options,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct,
        "explanation": question["explanation"],
        "original_question": question,
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


def print_study_summary(results: list[dict]) -> None:
    correct_count = sum(1 for item in results if item["is_correct"])
    total = len(results)
    percent = correct_count / total * 100 if total else 0

    print("\n" + "#" * 70)
    print("РЕЗУЛЬТАТ ПЕРШОГО ПРОХОДЖЕННЯ")
    print("#" * 70)
    print(f"Загальний бал: {correct_count}/{total}")
    print(f"Відсоток: {percent:.1f}%")


def run_regular_mode(
    selected_questions: list[dict],
    question_count: int,
    show_answer_immediately: bool,
) -> None:
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


def run_study_mode(selected_questions: list[dict], question_count: int) -> None:
    first_round_results = []
    wrong_questions = []

    print("\n" + "#" * 70)
    print("ПЕРШЕ ПРОХОДЖЕННЯ")
    print("#" * 70)

    for index, question in enumerate(selected_questions, start=1):
        result = ask_question(
            question=question,
            question_number=index,
            total=question_count,
            show_answer_immediately=True,
        )

        if result is None:
            print("\nНавчання завершено достроково.")
            break

        first_round_results.append(result)

        if not result["is_correct"]:
            wrong_questions.append(result["original_question"])

    if not first_round_results:
        print("\nНавчання завершено без жодної відповіді. Радикально, але не дуже навчально.")
        return

    print_study_summary(first_round_results)

    round_number = 2

    while wrong_questions:
        random.shuffle(wrong_questions)

        print("\n" + "#" * 70)
        print(f"ПОВТОРЕННЯ ПОМИЛОК. РАУНД {round_number}")
        print(f"Залишилось неправильних питань: {len(wrong_questions)}")
        print("#" * 70)

        current_round_questions = wrong_questions
        wrong_questions = []

        for index, question in enumerate(current_round_questions, start=1):
            result = ask_question(
                question=question,
                question_number=index,
                total=len(current_round_questions),
                show_answer_immediately=True,
            )

            if result is None:
                print("\nНавчання завершено достроково.")
                return

            if not result["is_correct"]:
                wrong_questions.append(result["original_question"])

        round_number += 1

    print("\n" + "#" * 70)
    print("УСІ ПОМИЛКИ ДОБИТІ")
    print("#" * 70)
    print("Ти пройшла всі неправильні питання правильно. Машина задоволена, але виду не подає.")


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

    quiz_mode = choose_quiz_mode()

    print("\nПід час тесту можна ввести stop або стоп, щоб завершити тест достроково.")

    if quiz_mode == "test":
        run_regular_mode(
            selected_questions=selected_questions,
            question_count=question_count,
            show_answer_immediately=False,
        )
    elif quiz_mode == "check":
        run_regular_mode(
            selected_questions=selected_questions,
            question_count=question_count,
            show_answer_immediately=True,
        )
    elif quiz_mode == "study":
        run_study_mode(
            selected_questions=selected_questions,
            question_count=question_count,
        )


if __name__ == "__main__":
    main()
