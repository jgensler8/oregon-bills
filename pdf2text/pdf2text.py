import luigi
import logging
import os
import PyPDF2
import re


class PDFPathSource(luigi.Task):
    def requires(self):
        return []

    def output(self):
        return luigi.LocalTarget("intermediate/files.txt")

    def run(self):
        logging.log(logging.INFO, "Starting PDFPathSource...")
        with self.output().open('w') as out:
            for root, dirs, files in os.walk('../data'):
                logging.log(logging.INFO, file)
                for f in files:
                    if f.endswith(".pdf"):
                        out.write(os.path.join(root, f))
                        out.write('\n')


class PDF2Text(luigi.Task):
    def requires(self):
        return [PDFPathSource()]

    def output(self):
        return luigi.LocalTarget("intermediate/pdf-per-line.txt")

    def run(self):
        num_lines = sum(1 for line in self.input()[0].open())

        with self.output().open('w') as out, self.input()[0].open() as paths:
            filenum = 0
            for path in paths:
                filenum += 1
                path = path.strip()
                reader = PyPDF2.PdfFileReader(path)
                for i in range(0, reader.getNumPages()):
                    page = reader.getPage(i)
                    text = page.extractText()
                    text = text.encode('utf-8').strip()
                    # Remove newlines
                    text = re.sub(r'\n', ' ', text, flags = re.MULTILINE)
                    out.write(text)
                    out.write('\n')

                self.set_status_message("Progress: {} / {};".format(filenum, num_lines))

class Text2SanitizedText(luigi.Task):
    def requires(self):
        return [PDF2Text()]

    def output(self):
        return luigi.LocalTarget("output/pdf-per-line-sanitized.txt")

    def run(self):
        num_lines = sum(1 for line in self.input()[0].open())

        with self.input()[0].open() as lines, self.output().open('w') as out:
            filenum = 0
            for line in lines:
                filenum += 1
                # Remove all digits
                line = re.sub(r'\d', ' ', line, flags = re.MULTILINE)
                # Remove extra space
                line = re.sub(r'\s+', ' ', line, flags = re.MULTILINE)
                # Remove non ascii chracters
                line = re.sub(r'[^0-9A-Za-z ]+', '', line, flags = re.MULTILINE)
                out.write(line)
                out.write('\n')

            self.set_status_message("Progress: {} / {};".format(filenum, num_lines))

if __name__ == '__main__':
    luigi.run()
