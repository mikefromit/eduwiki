__author__ = 'moonkey'

from models import *
from autoassess.diagnose.quesgen.common import QUESTION_TYPE_WHAT_IS
from autoassess.diagnose.quesgen.common import QUESTION_TYPE_MENTIONED_ITEM
import sys
import inspect

QUESTION_SET_TYPE = ("Prereq", "Mentioned", "Related")


def load_diagnose_question_set(
        topic, version, set_type="Prereq",
        with_meta_info=False,
        topical_first_question=True):
    if set_type == "Prereq":
        return load_diagnose_question_set_prereqs(topic, version)
    elif set_type == "Mentioned":
        return load_diagnose_question_set_mentioned(
            topic, version,
            with_meta_info=with_meta_info,
            topical_first_question=topical_first_question)


def load_diagnose_question_set_mentioned(
        topic, version,
        with_meta_info=False,
        topical_first_question=True):
    questions = []
    if topical_first_question:
        try:

            questions.append(load_question(
                topic, version=version, qtype=QUESTION_TYPE_WHAT_IS))
        except Exception as e:
            print >> sys.stderr, inspect.stack()[0][3]
            print >> sys.stderr, e

    try:
        question_set = QuestionSet.objects(set_topic=topic, version=version)[0]

        question_set_id = question_set.id

        for qt in question_set.related_topics:
            question = load_question(
                topic=qt, version=version,
                quiz_topic=topic, qtype=QUESTION_TYPE_MENTIONED_ITEM)
            print question
            questions.append(question)
        if not with_meta_info:
            return questions
        else:
            return questions, question_set_id
    except Exception as e:
        print >> sys.stderr, inspect.stack()[0][3]
        print >> sys.stderr, e


def load_diagnose_question_set_prereqs(topic, version):
    questions = [load_question(
        topic, version=version, qtype=QUESTION_TYPE_WHAT_IS)]
    try:
        prereqs = Prereq.objects(
            topic=topic,
            version=version)[0].prereqs
        for pre in prereqs:
            questions.append(load_question(topic=pre, version=version))
    except Exception:
        # error loading prereqs
        # just return the question related to the topic
        pass
    return questions


def save_diagnose_question_set(
        questions, version, force=False, set_type="Prereq"):
    """
    Warning: Always assuming the first topic is the main_topic.
    :param questions: topics of later questions are prereqs
            for the topic for the first question
    :return:
    """

    if set_type == "Prereq":
        return save_diagnose_question_set_prereqs(
            questions, version, force)
    elif set_type == "Mentioned":
        return save_diagnose_question_set_mentioned(
            questions, version, force)
    else:
        raise ValueError("The specified type does not exist.")


def save_diagnose_question_set_mentioned(questions, version, force=False):
    topics = [q['topic'] for q in questions]
    # Warning: !!! the first topic is the main_topic
    main_topic = topics[0]
    tosave_q_set = None
    if len(topics) > 1:
        appended_topics = topics
        if main_topic in appended_topics:
            appended_topics.remove(main_topic)
        mentioned_topics = appended_topics
        old_q_set = QuestionSet.objects.filter(
            set_topic=main_topic, version=version)
        if old_q_set and force:
            tosave_q_set = old_q_set[0]
        else:
            tosave_q_set = QuestionSet(set_topic=main_topic, version=version)

        if tosave_q_set:
            tosave_q_set.related_topics = mentioned_topics
            tosave_q_set.save()

    for q in questions:
        save_question(q, version=version, force=force, quiz_topic=main_topic)

    return tosave_q_set


def save_diagnose_question_set_prereqs(questions, version, force=False):
    # save prerequisites
    topics = [q['topic'] for q in questions]
    if len(topics) > 1:  # there are prereqs
        # Warning: !!!the first topic is the main_topic
        main_topic = topics[0]
        appended_topics = topics
        if main_topic in appended_topics:
            appended_topics.remove(main_topic)

        prereqs = appended_topics
        old_prereqs = Prereq.objects.filter(topic=main_topic, version=version)
        if old_prereqs:
            if not force:
                return False
            tosave_prereq = old_prereqs[0]
        else:
            tosave_prereq = Prereq(topic=main_topic, version=version)

        tosave_prereq.prereqs = prereqs
        # ListField([StringField(p) for p in prereqs])
        tosave_prereq.save()

    # save questions
    for q in questions:
        save_question(q, version=version, force=force)
    return True


def load_question(
        topic, version,
        qtype=QUESTION_TYPE_WHAT_IS, quiz_topic=None, verbose=False):
    """
    Note there is a mismatch between "load" and "save.
    We may saved questions with different types, but in "load",
    we only require topic as the input, and return the first questions
    :param topic:
    :return:
    """
    try:
        # # Version checking
        if version is None:
            wiki_question = \
                WikiQuestion.objects(
                    topic=topic, type=qtype,
                    quiz_topic=quiz_topic).order_by("-version")[0]
        else:
            wiki_question = WikiQuestion.objects(
                topic=topic, version=version,
                type=qtype, quiz_topic=quiz_topic)[0]

        question = format_question_to_show(wiki_question)
    except Exception as e:
        if verbose:
            print 'question loading failed for', topic, quiz_topic
        raise e
    return question


def save_question(question, version, quiz_topic=None, force=False):
    """
    Note there is a mismatch between "load" and "save.
    We may saved questions with different types, but in "load",
    we only require topic as the input, and return the first questions
    :param question:
    :param force:
    :return:
    """

    if quiz_topic == question['topic']:
        quiz_topic = None
    old_questions = WikiQuestion.objects.filter(
        topic=question['topic'],
        type=question['type'],
        version=version,
        quiz_topic=quiz_topic,
    )
    if old_questions:
        if force:
            wiki_question = old_questions[0]
        else:
            return False
    else:
        wiki_question = WikiQuestion(
            topic=question['topic'],
            type=question['type'],
            quiz_topic=quiz_topic,
        )
    if version:
        wiki_question.version = version

    wiki_question.question_text = question['question_text']
    wiki_question.choices = [a['text'] for a in question['choices']]
    for idx, c in enumerate(question['choices']):
        if c['correct']:
            wiki_question.correct_answer = idx

    wiki_question.save()
    return True


def format_question_to_show(wiki_question):
    # # Answers with idx, and correctness
    possible_answers = []
    for idx, c in enumerate(wiki_question['choices']):
        possible_answers.append({
            'text': c,
            'correct': True if idx == wiki_question[
                'correct_answer'] else False,
            'idx': idx,
        })

    # Random shuffle, the answer order will be different from time to time
    # random.shuffle(possible_answers)

    #
    question = {
        'id': wiki_question.id,
        'topic': wiki_question.topic,
        'type': wiki_question.type,
        'question_text': wiki_question.question_text,
        'choices': possible_answers
    }

    return question