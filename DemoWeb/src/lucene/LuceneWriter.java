package lucene;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.ListIterator;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field.Store;
import org.apache.lucene.document.IntPoint;
import org.apache.lucene.document.StoredField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.nlpir.lucene.cn.ictclas.NLPIRTokenizerAnalyzer;

public class LuceneWriter implements AutoCloseable {
	private Directory dir = null;
	private String dataPath = "";

	public LuceneWriter(String indexPath, String dataPath) {
		this.dataPath = dataPath;
		try {
			File file = new File(indexPath);
			dir = FSDirectory.open(file.toPath());
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	@Override
	public void close() throws Exception {
		dir.close();
	}

	/***
	 * 生成
	 * 
	 * @param question_ids
	 * @param questions
	 * @param answer_ids
	 * @param answers
	 */
	public void index(List<Integer> question_ids, List<String> questions, List<Integer> answer_ids,
			List<String> answers) {
		List<Document> docs = mergeQuestionAnswerPairs(question_ids, questions, answer_ids, answers);
		index(docs);
	}

	public void index(List<Document> docs) {
		Analyzer analyzer = new NLPIRTokenizerAnalyzer(dataPath, 1, "", "", false);
		IndexWriterConfig indexWriterConfig = new IndexWriterConfig(analyzer);
		try (IndexWriter indexWriter = new IndexWriter(dir, indexWriterConfig)) {
			indexWriter.addDocuments(docs);
//			ListIterator<Document> iter_docs = docs.listIterator();
//			while (iter_docs.hasNext()) {
//				Document doc = (Document) iter_docs.next();
//				indexWriter.addDocument(doc);
//				System.out.println(doc.getField("answer_id"));
//			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	/***
	 * 融合成问答对成为Document
	 * 
	 * @param question_ids
	 * @param questions
	 * @param answer_ids
	 * @param answers
	 * @return
	 */
	private List<Document> mergeQuestionAnswerPairs(List<Integer> question_ids, List<String> questions,
			List<Integer> answer_ids, List<String> answers) {
		assert question_ids.size() == questions.size() && question_ids.size() == answer_ids.size()
				&& question_ids.size() == answers.size();
		
		List<Document> res = new ArrayList<>(question_ids.size());
		ListIterator<Integer> iter_question_ids = question_ids.listIterator();
		ListIterator<String> iter_questions = questions.listIterator();
		ListIterator<Integer> iter_answer_ids = answer_ids.listIterator();
		ListIterator<String> iter_answers = answers.listIterator();
		while (iter_question_ids.hasNext()) {
			Document doc = new Document();
			int question_id = (int) iter_question_ids.next();
			int answer_id = (int) iter_answer_ids.next();
			doc.add(new IntPoint("question_id", question_id));
			doc.add(new StoredField("question_id", question_id));
			doc.add(new TextField("question", (String) iter_questions.next(), Store.NO));
			doc.add(new IntPoint("answer_id", answer_id));
			doc.add(new StoredField("answer_id", answer_id));
			doc.add(new TextField("answer", (String) iter_answers.next(), Store.NO));
			res.add(doc);
		}
		return res;
	}

}
