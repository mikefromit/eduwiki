from diagnose.prereq import find_direct_prereq
# Create your tests here.
topics = []
from diagnose import quesgen_sentstruct
from diagnose.util import wikipedia
from diagnose.util.nlp_util import NlpUtil

def test_sentence_extraction():
    # topic_max = 5
    # topics = []
    # with open("../../../random/topics/topic.txt", "rU") as topic_file:
    # topic_num = 0
    #     cat_line = False
    #     for t in topic_file.readlines():
    #         if topic_num >= topic_max:
    #             break
    #         if cat_line:
    #             cat_line = False
    #             print "Cat:" + t
    #             continue
    #
    #         t = t.strip('\n')
    #         if t.replace(" ", "") != "":
    #             topics.append(t)
    #             topic_num += 1
    #         else:
    #             cat_line = True
    #
    # sentences = []
    # for t in topics:
    #     page = wikipedia.page(t)
    #     # Extract sentences
    #     sents = quesgen_sentstruct.get_question_sentences(page)
    #     topic = page.title
    #     sents = sents[0:10]
    #     sents = [(sent, topic) for sent in sents]
    #     sentences += sents
    #
    # with open("../../../random/topics/sentences.txt", "w") as sentfile:
    #     for sent in sentences:
    #         print sent
    #         sentfile.write((sent[0]+"\n").encode("utf-8"))
    #         sentfile.write((sent[1]+"\n").encode("utf-8"))

    sentences = []
    with open("../../../random/topics/sentences.txt", "r") as sentfile:
        is_sent = True
        sent_tuple = [None, None]
        for sent in sentfile.readlines():
            if is_sent:
                sent_tuple[0] = sent.strip("\n")
                is_sent = False
            else:
                sent_tuple[1] = sent.strip("\n")
                sentences.append(list(sent_tuple))
                is_sent = True
                # print sentences[-1]

    for idx, sent in enumerate(sentences):
        # if idx > 10:
        #     break
        if sent[1] != 'Random forest':
            continue
        print "====================="
        print "Sentence:" + sent[0]
        question = quesgen_sentstruct.question_from_single_sentence(sent[0], sent[1])
        print "Question:" + str(question['stem'])
        print "Answer:" + str(question['answer'])


def generate_eduwiki_link():
    csvfile = open("../../../random/new.csv", "rU")
    for c in csvfile.readlines():
        topic = c.split(",")[0]
        # print topic
        topics.append(topic)

    # edufile = open("../../../random/eduwiki.csv", "w")
    #
    # for t in topics:
    # wikipage = WikipediaPage(title=t)
    # pres = find_direct_prereq(wikipage, 3)
    # line = t + ","
    # for p in pres:
    # line += p + ";"
    # edufile.write(line + "\n")
    # edufile.close()

    linkfile = open("../../../random/link.csv", "w")
    for t in topics:
        a = t.replace(' ', '+')
        link = "https://eduwiki.ml/autoassess/quiz/?q=" + a
        linkfile.write(t + "," + link + "\n")
    linkfile.close()

    csvfile.close()


def test_setentence_syntree():
    # draw_sentence_syntree("Reinforcement learning is known.")
    # draw_sentence_syntree("Reinforcement learning is known to be great.")
    draw_sentence_syntree("In the operations research and control literature, "
                          "the field where reinforcement learning methods are studied "
                          "is called approximate dynamic programming.")
def draw_sentence_syntree(sentence):
    nlutil = NlpUtil()
    parsed_sentence = nlutil.parsing(sentence)
    parsed_sentence.draw()



# TODO:: deal with the unicode issue, deal with the redirect, (inside the code)
# TODO:: find the positions of the manually selected prereqs. (here)

if __name__ == '__main__':
    # test_sentence_extraction()
    test_setentence_syntree()

