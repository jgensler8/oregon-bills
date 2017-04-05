import luigi
import pdf2text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

no_features = 1000
no_topics = 5

def display_topics(filenum, model, feature_names, no_top_words):
    alltopics=""

    for topic_idx, topic in enumerate(model.components_):
        topics = " ".join([feature_names[i]
                  for i in topic.argsort()[:-no_top_words - 1:-1]])
        alltopics += "%d,%d,%s\n" % (filenum, topic_idx, topics)

    alltopics = alltopics.encode('utf-8')
    return alltopics

class Text2LDATopics(luigi.Task):
    def requires(self):
        return [pdf2text.Text2SanitizedText()]

    def output(self):
        return luigi.LocalTarget("output/topics.csv")

    def run(self):
        num_lines = sum(1 for line in self.input()[0].open())

        with self.input()[0].open() as lines, self.output().open('w') as out:
            # Columns:
            # out.write('linenum,topicnum,topics\n')
            filenum = 0
            errors = 0
            for line in lines:
                filenum += 1
                tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
                document = line.split('.')
                try:
                    tf = tf_vectorizer.fit_transform(document)
                    tf_feature_names = tf_vectorizer.get_feature_names()

                    if tf is not None:
                        lda = LatentDirichletAllocation(n_topics=no_topics, max_iter=5, learning_method='online',
                                                        learning_offset=50., random_state=0).fit(tf)

                        # out.write(tf_feature_names)
                        out.write(display_topics(filenum, lda, tf_feature_names, no_topics))
                    else:
                        errors += 1
                except:
                    errors += 1
                self.set_status_message("Progress: {} / {}; Errors: {}".format(filenum, num_lines, errors))



if __name__ == '__main__':
    luigi.run()
