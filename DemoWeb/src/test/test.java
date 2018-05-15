package test;

import java.util.HashMap;
import java.util.List;
import java.util.ListIterator;

import lucene.LuceneReader;
import tool.DBTool;
import tool.PropertyTool;

public class test {

	
	public static void main(String[] args) {
		HashMap<String, String> parameters = PropertyTool.getProperties("F:/Workspace_Java/DemoWeb/src/config.properties");
		String url = String.format(
				"jdbc:mysql://%s:%s/%s?useUnicode=true&autoReconnect=true&rewriteBatchedStatements=true",
				parameters.get("host"), parameters.get("port"), parameters.get("database"));
		try (DBTool dbTool = new DBTool(url, parameters.get("user"), parameters.get("password"));
				LuceneReader reader = new LuceneReader(parameters.get("index_path"), parameters.get("data_path"))) {
			List<Long> query_ids = dbTool.getQueryIDs();
			List<String> querys = dbTool.getQuestionsByQuestionIDs(query_ids);
			assert query_ids.size() == querys.size();
			ListIterator<Long> query_id_iter = query_ids.listIterator();
			ListIterator<String> query_iter = querys.listIterator();
			int count = 0;
			while (query_id_iter.hasNext()) {
				long query_id = (long) query_id_iter.next();
				String query = (String) query_iter.next();
				List<Long> candidate_ids = reader.searchQuestions(query, 501);
				candidate_ids.remove(query_id);
				if (candidate_ids.size() == 501) {
					// 去掉最后一个
					candidate_ids.remove(500);
				}
				assert candidate_ids.size() == 500;
				dbTool.insertCandididates(query_id, candidate_ids);
				System.out.println(++count);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

}
