package test;

import java.util.HashMap;
import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import lucene.LuceneReader;
import tool.PropertyTool;

public class testLuceneReader {
	LuceneReader reader = null;
	
	@Before
	public void init() {
		HashMap<String, String> config = PropertyTool.getProperties("F:/Workspace_Java/DemoWeb/src/config.properties");
		reader = new LuceneReader(config.get("index_path"), config.get("data_path"));
	}
	
	@After
	public void autoClose() {
		try {
			reader.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	@Test
	public void searchQuestions() {
		List<Long> question_ids = null;
		try {
			String query = "关税是什么";
			question_ids = reader.searchQuestions(query, 10);
			for (Long question_id : question_ids) {
				System.out.println(question_id);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
