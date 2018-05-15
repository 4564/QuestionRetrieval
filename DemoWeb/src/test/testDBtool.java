package test;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import tool.DBTool;
import tool.PropertyTool;

public class testDBtool {
	DBTool tool = null;
	
	@Before
	public void init() {
		HashMap<String, String> config = PropertyTool.getProperties("F:/Workspace_Java/DemoWeb/src/config.properties");
		String url = String.format(
				"jdbc:mysql://%s:%s/%s?useUnicode=true&autoReconnect=true&rewriteBatchedStatements=true",
				config.get("host"), config.get("port"), config.get("database"));
		tool = new DBTool(url, config.get("user"), config.get("password"));
	}
	
	@After
	public void autoClose() {
		try {
			tool.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	@Test
	public void getQuestionIDRandom() {
		System.out.println(tool.getQuestionIDRandom());
		System.out.println(tool.getQuestionIDRandom());
		System.out.println(tool.getQuestionIDRandom());
	}
	
	@Test
	public void getQuestionByQuestionID() {
		System.out.println(tool.getQuestionByQuestionID(9633101L));
	}
	
	@Test
	public void getQuestionsByQuestionIDs() {
		List<Long> ids = new LinkedList<>();
		ids.add(9633101L);
		ids.add(635025833L);
		ids.add(548293934L);
		List<String> questions = tool.getQuestionsByQuestionIDs(ids);
		for (String question : questions) {
			System.out.println(question);
		}
	}
	
	@Test
	public void insertQueryID() {
		System.out.println(tool.insertQueryID(1L));
		System.out.println(tool.insertQueryID(1L));
	}
	
	@Test
	public void insertCandidates() {
		List<Long> candidate_ids = new LinkedList<>();
		candidate_ids.add(5L);
		candidate_ids.add(6L);
		System.out.println(tool.insertCandididates(1L, candidate_ids));
	}
	
	@Test
	public void getQueryIDs() {
		System.out.println(tool.getQueryIDs());
	}

	@Test
	public void getUnmarkQueryID() {
		System.out.println(tool.getUnmarkQueryID(1));
	}
	
	@Test
	public void getMarkQueryIDs() {
		System.out.println(tool.getMarkCandidateIDs(5793896L));
	}
	
	@Test
	public void getFlags() {
		long query_id = 565452L;
		List<Long> candidate_ids = tool.getMarkCandidateIDs(query_id);
		List<Integer> candidate_flags = tool.getFlags(query_id, candidate_ids);
		System.out.println(candidate_flags);
	}
}
