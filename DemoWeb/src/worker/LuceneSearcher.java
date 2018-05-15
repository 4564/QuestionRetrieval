package worker;

import java.io.File;
import java.io.FileOutputStream;
import java.util.HashMap;
import java.util.List;
import java.util.ListIterator;

import lucene.LuceneReader;
import tool.DBTool;
import tool.PropertyTool;

public class LuceneSearcher {

	public static void main(String[] args) {
		HashMap<String, String> parameters = PropertyTool.getProperties("F:/Workspace_Java/DemoWeb/src/config.properties");
		String url = String.format(
				"jdbc:mysql://%s:%s/%s?useUnicode=true&autoReconnect=true&rewriteBatchedStatements=true",
				parameters.get("host"), parameters.get("port"), parameters.get("database"));
		File result = new File("F:/Data/Chinese/Result/lucene_result.tsv");
		try (DBTool dbTool = new DBTool(url, parameters.get("user"), parameters.get("password"));
				LuceneReader reader = new LuceneReader(parameters.get("index_path"), parameters.get("data_path"));
				FileOutputStream out = new FileOutputStream(result, false)) {
			List<Long> query_ids = dbTool.getQueryIDs();
//			List<Long> query_ids = new LinkedList<>();
//			query_ids.add(291901170L);
			List<String> querys = dbTool.getQuestionsByQuestionIDs(query_ids);
			assert query_ids.size() == querys.size();
			ListIterator<Long> query_id_iter = query_ids.listIterator();
			ListIterator<String> query_iter = querys.listIterator();
			int count = 0;
			while (query_id_iter.hasNext()) {
				long query_id = (long) query_id_iter.next();
				String query = (String) query_iter.next();
				List<Long> candidate_ids = reader.searchQuestions(query, 11);
				candidate_ids.remove(query_id);
				if (candidate_ids.size() == 11) {
					// 去掉最后一个
					candidate_ids.remove(10);
				}
				if (candidate_ids.size() != 10) {
					System.out.println(query_id + "不满10个！");
				}
				ListIterator<Long> candidate_id_iter = candidate_ids.listIterator();
				out.write(String.format("%d", query_id).getBytes("UTF-8"));
				while (candidate_id_iter.hasNext()) {
					long candidate_id = (long) candidate_id_iter.next();
					out.write(String.format("\t%d", candidate_id).getBytes("UTF-8"));
				}
				out.write("\n".getBytes("UTF-8"));
				System.out.println(++count);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
