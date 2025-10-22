import argparse
import copy
import csv
import json

import click


def init_argparser():
    """
    Initialize the command line parser.

    :return: the command line parser
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Joins the output of LDA in a single file"
        " that is suitable the manual verification"
    )
    parser.add_argument(
        "abstracts",
        action="store",
        type=str,
        help="CSV file containing the abstracts.",
    )
    parser.add_argument(
        "terms_topics",
        action="store",
        type=str,
        help="JSON file containing the association between "
        "terms and topics.",
    )
    parser.add_argument(
        "docs_topics",
        action="store",
        type=str,
        help="JSON file containing the association between docs"
        " and topics.",
    )
    parser.add_argument(
        "--output", "-o", action="store", type=str, help="Output file"
    )
    return parser


def csv_to_list_of_dicts(file_name):
    with open(file_name, "r") as infile:
        csv_reader = csv.DictReader(infile, delimiter="\t")
        data = []
        for item in csv_reader:
            data.append(item)
    return data


def organize_topics(loaded_topics):
    # for each topic keeps the name and the list of terms
    topics = {}
    for p in loaded_topics:
        identifier = p
        loaded_prob = loaded_topics[p]["terms_probability"]
        probab = []
        for pp in loaded_prob:
            probab.append((pp, loaded_prob[pp]))
        sorted_by_second = sorted(probab, key=lambda tup: tup[1], reverse=True)
        topics[identifier] = {
            "name": loaded_topics[p]["name"],
            "terms": sorted_by_second[:10],
        }
    return topics


def colorize_abstract(doc):
    """Colorize the abstract and the terms of a single document."""
    palette = ["red", "green", "yellow", "blue"]
    color_n = 0
    ab = doc["abstract_short"].split(" ")
    ab_colored = copy.deepcopy(ab)
    for _, topic in doc["topics_data"].items():
        colorize_topic = False
        colored_terms = copy.deepcopy(topic[2])
        for i, term in enumerate(topic[2]):
            colorize_term = False
            for j, token in enumerate(ab):
                n = term.count("_")
                # manages multi-grams
                if n > 0:
                    if j >= len(ab) - n:
                        continue
                    aggr = "_".join(ab[j: j + n + 1])
                    if aggr == term:
                        for index in range(j, j + n + 1):
                            ab_colored[index] = click.style(
                                ab[index], fg=palette[color_n]
                            )
                        colorize_term = True
                # manages uni-grams
                if term == token:
                    ab_colored[j] = click.style(token, fg=palette[color_n])
                    colorize_term = True
                # manages acronyms
                if "@" + term + "@" == token:
                    ab_colored[j] = click.style(token, fg=palette[color_n])
                    colorize_term = True
            if colorize_term:
                colored_terms[i] = click.style(term, fg=palette[color_n])
                colorize_topic = True
        topic.append(colored_terms)
        if colorize_topic:
            color_n += 1
            color_n = color_n % len(palette)

    return ab_colored


def join_lda_info(loaded_topics, docs, abstracts):
    """
    Joins the information about the topics assigned to each document

    :param loaded_topics: information about the topics
    :type loaded_topics: dict
    :param docs: association between documents and topics
    :type docs: list[dict]
    :param abstracts: list of abstracts
    :type abstracts: list[dict]
    """

    topics = organize_topics(loaded_topics)

    for d in docs:
        d["abstract"] = abstracts[d["id"]]["abstract"]
        d["abstract_short"] = abstracts[d["id"]]["abstract_lem"]
        d["abstract_filtered"] = abstracts[d["id"]]["abstract_filtered"]
        top = []
        for t in d["topics"]:
            top.append([t, d["topics"][t]])
        if len(top) == 0:
            d["most_relevant_topic"] = {"name": "", "relevance": -1}
            continue
        sorted_by_second = sorted(top, key=lambda tup: tup[1], reverse=True)
        max_relevance = max([x[1] for x in sorted_by_second])
        # saves this information for sorting later
        d["most_relevant_topic"] = {
            "name": sorted_by_second[0][0],
            "relevance": max_relevance,
        }
        d["topics_data"] = {}
        for t in sorted_by_second:
            if t[1] < max_relevance / 10.0:
                break
            key = t[0]
            name = topics[key]["name"]
            terms = [t[0] for t in topics[key]["terms"]]
            t.append(terms)
            d["topics_data"][name] = t
        d["colored_abstract"] = colorize_abstract(d)
    return docs


def output_colorized_text_file(docs, output=None):
    """
    :param output: output file. If None, stdout is used
    :type output: str or None
    """
    if output is not None:
        output_file = open(output, "w")
    else:
        output_file = None

    for d in docs:
        print(f'{d["id"]} - {d["title"]}', file=output_file)
        if "topics_data" not in d:
            print("   *** Skipping: no topics ***\n", file=output_file)
            continue
        print(file=output_file)
        print(d["abstract"], file=output_file)
        print(file=output_file)
        print(" ".join(d["colored_abstract"]), file=output_file)
        print(file=output_file)
        print(d["abstract_filtered"], file=output_file)
        print(file=output_file)
        for k, v in d["topics_data"].items():
            print(
                f"{100*v[1]:7.1f}% | {k} | {' - '.join(v[3])}",
                file=output_file,
            )
        print(file=output_file)
        print("-" * 10, "\n", file=output_file)


def main():
    args = init_argparser().parse_args()
    terms_topics = args.terms_topics
    docs_topics = args.docs_topics
    output = args.output

    with open(terms_topics) as topics_file:
        loaded_topics = json.load(topics_file)

    with open(docs_topics) as docs_file:
        docs = json.load(docs_file)

    abstracts = csv_to_list_of_dicts(args.abstracts)

    # docs = docs[1:2]

    docs = join_lda_info(loaded_topics, docs, abstracts)

    # sort by ascending topic, then by descending relevance,
    # then by ascending id
    docs.sort(
        key=lambda datum: (
            datum["most_relevant_topic"]["name"],
            -datum["most_relevant_topic"]["relevance"],
            datum["id"],
        )
    )

    output_colorized_text_file(docs, output=output)


if __name__ == "__main__":
    main()
