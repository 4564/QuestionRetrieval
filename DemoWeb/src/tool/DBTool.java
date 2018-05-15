package tool;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.ListIterator;

import org.apache.lucene.document.Document;
import org.apache.lucene.document.IntPoint;
import org.apache.lucene.document.StoredField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.document.Field.Store;

import lucene.LuceneWriter;

public class DBTool implements AutoCloseable {
	private Connection conn = null;

	/***
	 * 
	 * @param url
	 * @param user
	 * @param password
	 */
	public DBTool(String url, String user, String password) {
		try {
			Class.forName("com.mysql.jdbc.Driver");
			conn = DriverManager.getConnection(url, user, password);
		} catch (ClassNotFoundException e) {
			System.out.println("MySQL驱动加载失败！");
			e.printStackTrace();
		} catch (SQLException e) {
			System.out.println("MySQL连接出错！");
			e.printStackTrace();
		}
	}

	/***
	 * 用列表获取所有问答对数据，通过List返回
	 * @param question_ids 
	 * @param questions
	 * @param answer_ids 
	 * @param answers
	 * @param ids 提供的answer_ids
	 * @deprecated
	 */
	public void getQAPairsByAnswerID(List<Long> question_ids, List<String> questions, List<Long> answer_ids,
			List<String> answers, List<Long> ids) {
		String sql = "select question_id, question, answer_id, answer from qa where answer_id=?";
		try (PreparedStatement  ps = conn.prepareStatement(sql)) {
			ListIterator<Long> iter_ids = ids.listIterator();
			while (iter_ids.hasNext()) {
				ps.setLong(1, (long) iter_ids.next());
				ResultSet rs = ps.executeQuery();
				if (rs.next()) {
					question_ids.add(rs.getLong("question_id"));
					questions.add(rs.getString("question"));
					answer_ids.add(rs.getLong("answer_id"));
					answers.add(rs.getString("answer"));
				}
			}
		} catch (SQLException e) {
			e.printStackTrace();
		}
	}
	
	/***
	 * 随机获得一个问题ID
	 * @return 问题ID
	 */
	public long getQuestionIDRandom() {
		long result = -1;
		try (Statement stmt = conn.createStatement()){
			ResultSet rs = stmt.executeQuery("select question_id from qa order by rand() limit 1");
			if (rs.next()) {
				result = rs.getLong("question_id");
			}
			rs.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return result;
	}
	
	/***
	 * 根据问题ID获取问题
	 * @return 问题
	 */
	public String getQuestionByQuestionID(long question_id) {
		String question = null;
		try (Statement stmt = conn.createStatement()){
			String sql = String.format("select question from qa where question_id=%d limit 1", question_id);
			ResultSet rs = stmt.executeQuery(sql);
			if (rs.next()) {
				question = rs.getString("question");
			}
			rs.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return question;
	}
	
	/***
	 * 用问题ID列表获取所有问题列表
	 * @param question_ids 提供的问题ID列表
	 * @return questions 问题列表
	 */
	public List<String> getQuestionsByQuestionIDs(List<Long> question_ids) {
		List<String> questions = new LinkedList<>();
		ListIterator<Long> iter_ids = question_ids.listIterator();
		while (iter_ids.hasNext()) {
			questions.add(getQuestionByQuestionID((long)iter_ids.next()));
		}
		return questions;
	}
	
	/***
	 * 获取全部查询ID
	 * @return 查询 ID
	 */
	public List<Long> getQueryIDs() {
		List<Long> query_ids = new LinkedList<>();
		try (Statement stmt = conn.createStatement()){
			ResultSet rs = stmt.executeQuery("select id from query");
			while (rs.next()) {
				query_ids.add(rs.getLong("id"));
			}
			rs.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return query_ids;
	}
	
	/***
	 * 获取一个未标记的查询ID
	 * @return query_id
	 */
	public long getUnmarkQueryID(int flag) {
		long query_id = -1;
		String sql = String.format("select query_id from candidate where flag=-1 or flag=%d group by query_id order by query_id limit 1", 3 - flag);
		if (flag == 3) 
			sql = "select query_id from candidate where flag=3 group by query_id order by query_id limit 1";
		try (Statement stmt = conn.createStatement()){
			ResultSet rs = stmt.executeQuery(sql);
			if (rs.next()) {
				query_id = rs.getLong("query_id");
			}
			rs.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return query_id;
	}
	
	/***
	 * 根据查询ID获取其需要标记和已经标记的候选问题ID
	 * @param query_id 查询ID
	 * @return
	 */
	public List<Long> getMarkCandidateIDs(long query_id) {
		List<Long> candidate_ids = new LinkedList<>();
		String sql = String.format("select candidate_id from candidate where flag!=0 and query_id=%d", query_id);
		try (Statement stmt = conn.createStatement()){
			ResultSet rs = stmt.executeQuery(sql);
			while (rs.next()) {
				candidate_ids.add(rs.getLong("candidate_id"));
			}
			rs.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return candidate_ids;
	}
	
	/***
	 * 获取对应flag
	 * @param query_id 查询ID
	 * @param candidate_ids 候选
	 * @return flags
	 */
	public List<Integer> getFlags(long query_id, List<Long> candidate_ids) {
		List<Integer> flags = new LinkedList<>();
		String sql = "select flag from candidate where query_id=? and candidate_id=?";
		try (PreparedStatement preStmt = conn.prepareStatement(sql)) {
			for (long candidate_id : candidate_ids) {
				preStmt.setLong(1, query_id);
				preStmt.setLong(2, candidate_id);
				ResultSet rs = preStmt.executeQuery();
				if (rs.next()) {
					flags.add(rs.getInt("flag"));
				}
			}
		} catch (SQLException e) {
			e.printStackTrace();
		}
		return flags;
	}
	
	public List<Integer> getRelevance(long query_id, List<Long> candidate_ids) {
		List<Integer> relevance = new LinkedList<>();
		String sql = "select relevance from candidate where query_id=? and candidate_id=?";
		try (PreparedStatement preStmt = conn.prepareStatement(sql)) {
			for (long candidate_id : candidate_ids) {
				preStmt.setLong(1, query_id);
				preStmt.setLong(2, candidate_id);
				ResultSet rs = preStmt.executeQuery();
				if (rs.next()) {
					relevance.add(rs.getInt("relevance"));
				}
			}
		} catch (SQLException e) {
			e.printStackTrace();
		}
		return relevance;
	}
	
	/***
	 * 插入查询ID
	 * @param query_id 
	 * @return 成功返回 true
	 */
	public boolean insertQueryID(long query_id) {
		int num = -1;
		String sql = "insert ignore into query(id) values(?)";
		try (PreparedStatement preStmt = conn.prepareStatement(sql)) {
			preStmt.setLong(1, query_id);
			num = preStmt.executeUpdate();
		} catch (SQLException e) {
			e.printStackTrace();
		}
		return num == 1;
	}
	
	/***
	 * 插入候选集
	 * @param query_id 查询ID
	 * @param candidate_ids 候选ID
	 * @return 影响行数
	 */
	public int insertCandididates(Long query_id, List<Long> candidate_ids) {
		int num = 0;
		String sql = "insert ignore into candidate(query_id, candidate_id) values(?, ?)";
		try (PreparedStatement preStmt = conn.prepareStatement(sql)) {
			for (Long candidate_id : candidate_ids) {
				preStmt.setLong(1, query_id);
				preStmt.setLong(2, candidate_id);
				num += preStmt.executeUpdate();
			}
		} catch (SQLException e) {
			e.printStackTrace();
		}
		return num;
	}
	
	/***
	 * 更新相关性
	 * @param query_id 查询Id
	 * @param candidate_id 候选问题ID
	 * @param relevance 相关性
	 * @param flag 标识位
	 * @return 成功 true 失败 false
	 */
	public boolean update_relevance(long query_id, long candidate_id, int relevance, int flag) {
		// 先获取原来的情况
		int num = 0;
		String sql = "update candidate set relevance=?, flag=? where query_id=? and candidate_id=?";
		try (PreparedStatement preStmt = conn.prepareStatement(sql)) {
			preStmt.setInt(1, relevance);
			preStmt.setInt(2, flag);
			preStmt.setLong(3, query_id);
			preStmt.setLong(4, candidate_id);
			num = preStmt.executeUpdate();
		} catch (SQLException e) {
			e.printStackTrace();
		}
		return num == 1;
	}
	
	/***
	 * 数据太多分批索引
	 * question_id < 20000000
	 * question_id > 20000000 and question_id < 400000000
	 * @param writer
	 */
	public void index(LuceneWriter writer) {
		String sql = "select question_id, question, answer_id, answer from qa where question_id > 400000000"; 
		try (Statement stmt = conn.createStatement(); ResultSet rs = stmt.executeQuery(sql);) {
			int count = 0;
			List<Document> docs = new ArrayList<Document>(21000);
			while (rs.next()) {
				count++;
				Document doc = new Document();
				doc.add(new IntPoint("question_id", rs.getInt("question_id"))); 
				doc.add(new StoredField("question_id", rs.getInt("question_id")));
				doc.add(new TextField("question", rs.getString("question"), Store.NO));
				doc.add(new IntPoint("answer_id", rs.getInt("answer_id")));
				doc.add(new StoredField("answer_id", rs.getInt("answer_id")));
				doc.add(new TextField("answer", rs.getString("answer"), Store.NO));
				docs.add(doc);
				if (count % 20000 == 0) {
					writer.index(docs);
					docs = new ArrayList<Document>(21000);
					System.out.println(count);
				}
			}
			if (docs.size() > 0) {
				writer.index(docs);
				System.out.println(count);
			}
		} catch (SQLException e) {
			e.printStackTrace();
		}
	}
	
	@Override
	public void close() throws Exception {
		if (conn != null && !conn.isClosed())
			conn.close();
	}
}
