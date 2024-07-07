import streamlit as st
import openai

client = openai
client.api_key = st.secrets['OPENAI_API_KEY']

# Read CSS file
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'characteristics' not in st.session_state:
    st.session_state.characteristics = []
if 'category' not in st.session_state:
    st.session_state.category = None
if 'guesses' not in st.session_state:
    st.session_state.guesses = 0
if 'yes_answers' not in st.session_state:
    st.session_state.yes_answers = 0
if 'no_answers' not in st.session_state:
    st.session_state.no_answers = 0
if 'category_confirmed' not in st.session_state:
    st.session_state.category_confirmed = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'correct_guess' not in st.session_state:
    st.session_state.correct_guess = False
if 'guessed_object' not in st.session_state:
    st.session_state.guessed_object = None
if 'show_image' not in st.session_state:
    st.session_state.show_image = False
if 'final_guess' not in st.session_state:
    st.session_state.final_guess = False

def ask_question():
    sysprompt = """
    You are an AI as powerful as Akinator. Ask one question at a time to guess the character, animal, or object the user is thinking of.
    Only ask questions or guesses that can be answered with 'Yes', 'No', 'Don't know', 'Probably', or 'Probably not'. 
    Do not ask about personal or unrelated information. Focus on attributes, behaviors, or characteristics related to the category.
    Start by asking broad questions to narrow down the possibilities within the category.
    For example, if the category is 'Character', Sakinator can ask if the character is either real or Sakinator can also ask if the character is fictional, and then narrow down by origin.
    If the category is 'Character', and the user is thinking of a real person, Sakinator can ask if the character is a male or female, and then narrow down by gender.
    If the category is 'Character', and the user is thinking of a fictional character, Sakinator can ask if the character is an anime character or superhero or a villan, and then narrow down by type.
    Then, if the category is'Animal', ask questions like 'Does it fly?' or 'Is it a domestic animal?'.
    If the category is 'Animal', then Sakinator can ask questions like 'Is it a cat?' or 'Is it a dog?'.
    If the category is 'Animal', and  if users answer these two 'Is it a cat?' and 'Is it a dog?' questions with 'No', Sakinator may ask these 'Is it a type of cat?' or 'Is it a type of dog?' to narrow down to the type of the animal.
    If the category is 'Object', Sakinator can ask questions like 'Is it used in the kitchen?' or 'Is it electronic?' or 'Is it non-electric?'.
    """
    user_prompt = f"Category: {st.session_state.category}. "
    for q, a in zip(st.session_state.questions, st.session_state.answers):
        user_prompt += f"Q: {q} A: {a}. "

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": sysprompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=80
    )
    question = response.choices[0].message.content.strip()

    prefixes_to_remove = ["Q:", "Sakinator:"]
    for prefix in prefixes_to_remove:
        if question.startswith(prefix):
            question = question[len(prefix):].strip()

    return question

def generate_image(description):
    response = client.images.generate(
        prompt=description,
        n=1,
        size="512x512"
    )
    image_url = response.data[0].url
    return image_url

def determine_guessed_object():
    if st.session_state.category == "Object":
        if "used to eat" in " ".join(st.session_state.answers):
            return "spoon"
        elif "used to write" in " ".join(st.session_state.answers):
            return "pen"
    elif st.session_state.category == "Animal":
        if "flies" in " ".join(st.session_state.answers):
            return "bird"
        elif "domestic" in " ".join(st.session_state.answers):
            return "cat"
    elif st.session_state.category == "Human":
        if "scientist" in " ".join(st.session_state.answers):
            return "Albert Einstein"
        elif "actor" in " ".join(st.session_state.answers):
            return "Tom Hanks"
    return "unknown"

def clearance(user_input):
    return user_input.strip()

def reset():
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.characteristics = []
    st.session_state.category = None
    st.session_state.guesses = 0
    st.session_state.yes_answers = 0
    st.session_state.no_answers = 0
    st.session_state.category_confirmed = False
    st.session_state.current_question = None
    st.session_state.correct_guess = False
    st.session_state.guessed_object = None
    st.session_state.show_image = False
    st.session_state.final_guess = False
    st.experimental_rerun()

def main():
    st.markdown('<div class="title">Sakinator</div>', unsafe_allow_html=True)

    if not st.session_state.category_confirmed:
        st.markdown('<div class="subtitle">Select the next game thematic</div>', unsafe_allow_html=True)
        st.session_state.category = st.selectbox("", ["Character", "Animal", "Object"])

        if st.button("Next", key="next_button"):
            st.session_state.category_confirmed = True
            st.experimental_rerun()
    else:
        if st.session_state.correct_guess:  # Check if Sakinator guessed correctly
            st.markdown(f'<div class="guessed-object">My guess is, the {st.session_state.category.lower()} you are thinking is {st.session_state.guessed_object}.</div>', unsafe_allow_html=True)
            st.session_state.correct_guess = False  # Reset to handle the correct flow for user confirmation
            
        # Set to only 10 guesses for presentation purpose
        if st.session_state.guesses < 10 and not st.session_state.final_guess:
            if not st.session_state.current_question:
                st.session_state.current_question = ask_question()

            st.markdown(f'<div class="question">{st.session_state.guesses + 1}. {st.session_state.current_question}</div>', unsafe_allow_html=True)

            answer = st.radio(
                "",
                ["Yes", "No", "Don't know", "Probably", "Probably not"],
                key="user_answer",
                index=2,
                horizontal=True
            )

            cols = st.columns(2)
            with cols[0]:
                if st.button("Submit"):
                    st.session_state.questions.append(st.session_state.current_question)
                    st.session_state.answers.append(answer)
                    st.session_state.characteristics.append(f"{st.session_state.current_question} {answer}")
                    st.session_state.guesses += 1
                    if answer == "No":
                        st.session_state.no_answers += 1
                    elif answer == "Yes":
                        st.session_state.yes_answers += 1
                    st.session_state.current_question = None

                    if st.session_state.guesses > 5 and st.session_state.yes_answers > st.session_state.no_answers:
                        guessed_object = determine_guessed_object()
                        if guessed_object != "unknown":
                            st.session_state.correct_guess = True
                            st.session_state.guessed_object = guessed_object

                    st.experimental_rerun()
            with cols[1]:
                if st.button("Reset"):
                    reset()

            # Check if the object is guessed correctly
            if st.session_state.correct_guess:
                st.markdown(f'<div class="guessed-object">I knew it, the {st.session_state.category.lower()} you are thinking is {st.session_state.guessed_object}.</div>', unsafe_allow_html=True)
                user_input = st.session_state.guessed_object
                if user_input:
                    cols = st.columns(2)
                    with cols[0]:
                        if st.button("Show Image"):
                            clearance_input = clearance(user_input)
                            prompt = f"Show image of {clearance_input}"
                            image_url = generate_image(prompt)
                            if image_url:
                                st.image(image_url)
                    with cols[1]:
                        if st.button("Reset"):
                            reset()

        else:
            st.markdown('<div class="subtitle">I give up! What is it then?</div>', unsafe_allow_html=True)
            user_input = st.text_input("")
            if user_input:
                cols = st.columns(2)
                with cols[0]:
                    if st.button("Show Image"):
                        clearance_input = clearance(user_input)
                        prompt = f"Show image of {clearance_input}"
                        image_url = generate_image(prompt)
                        if image_url:
                            st.image(image_url)
                with cols[1]:
                    if st.button("Reset", key="reset_button"):
                        reset()

if __name__ == "__main__":
    main()
