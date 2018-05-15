package lucene;

import java.io.File;
import java.io.IOException;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;

import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.queryparser.classic.MultiFieldQueryParser;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.search.BooleanClause.Occur;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.nlpir.lucene.cn.ictclas.NLPIRTokenizerAnalyzer;

public class LuceneReader implements AutoCloseable {
	private Directory dir = null;
	private String dataPath = "";
	
	public LuceneReader(String indexPath, String dataPath) {
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

	public List<Long> searchQuestions(String q, int n) {
		List<Long> question_ids = new LinkedList<>();
		try (DirectoryReader reader = DirectoryReader.open(dir)){
			IndexSearcher searcher = new IndexSearcher(reader);
			String[] fields = {"question", "answer"};
			Occur[] occurs = {Occur.SHOULD, Occur.SHOULD}; 
			Query query = null;
			try {
				query = MultiFieldQueryParser.parse(q, fields, occurs, new NLPIRTokenizerAnalyzer(dataPath, 1, "", "", false));
			} catch (ParseException e) {
				e.printStackTrace();
			}
			TopDocs tds = searcher.search(query, n * 40);
			Set<Long> temp = new HashSet<>(n);
			for(ScoreDoc sd: tds.scoreDocs){
				Document doc = searcher.doc(sd.doc);
				if (temp.size() < n) {
					long question_id = Long.parseLong(doc.get("question_id"));
					if (!temp.contains(question_id)) {
						temp.add(question_id);
						question_ids.add(question_id);
					}
				} else {
					break;
				}
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		return question_ids;
	}
}
