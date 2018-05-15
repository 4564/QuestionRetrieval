<%@page import="java.util.LinkedList"%>
<%@page import="java.util.ListIterator"%>
<%@page import="lucene.LuceneReader"%>
<%@page import="java.util.List"%>
<%@page import="tool.DBTool"%>
<%@page import="tool.PropertyTool"%>
<%@page import="java.util.HashMap"%>
<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>挑选查询</title>
</head>
<body>
	<%
	String configPath = pageContext.getServletContext().getRealPath("/config.properties");
	HashMap<String, String> parameters = PropertyTool.getProperties(configPath);
	String url = String.format(
			"jdbc:mysql://%s:%s/%s?useUnicode=true&autoReconnect=true&rewriteBatchedStatements=true",
			parameters.get("host"), parameters.get("port"), parameters.get("database"));
	DBTool dbTool = new DBTool(url, parameters.get("user"), parameters.get("password"));
	String query_id_str = request.getParameter("query_id");
	boolean flag = false;
	int num = 0;
	if (query_id_str != null){
		String[] candidate_ids_str = request.getParameterValues("candidate_ids");
		List<Long> candidate_ids = new LinkedList<Long>();
		for (String candidate_id_str : candidate_ids_str) {
			candidate_ids.add(Long.parseLong(candidate_id_str));
		}
		flag = dbTool.insertQueryID(Long.parseLong(query_id_str));
		num = dbTool.insertCandididates(Long.parseLong(query_id_str), candidate_ids);
	}
	long query_id = -1;
	String query = null;
	List<Long> question_ids = null;
	try {
		LuceneReader reader = new LuceneReader(parameters.get("index_path"), parameters.get("data_path"));
		while (true) {
			query_id = dbTool.getQuestionIDRandom();
			query = dbTool.getQuestionByQuestionID(query_id);
			question_ids = reader.searchQuestions(query, 1001);
			if (question_ids.size() == 1001) {
				question_ids.remove(query_id);
				break;
			}
			assert question_ids.size() == 1000;
		}
		reader.close();
	} catch (Exception e) {
		e.printStackTrace();
	}
 	// System.out.println(question_ids.size());
	List<String> questions = dbTool.getQuestionsByQuestionIDs(question_ids.subList(0, 20));
	dbTool.close();
	if (flag) {
	%>
		插入<%=query_id_str %><br>
	<% 
	}
	%>
	<%=query_id %>: <%=query %>
	<form action = "selectQuery.jsp" method="post">
		<input name="query_id" type="hidden" value=<%=query_id%>>
		<%
		for (long question_id : question_ids){
		%>
			<input name="candidate_ids" type="hidden" value=<%=question_id%>>
		<%
		}
		%>
		<input type="submit" value="添加">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
		<input type=button value="刷新" onclick="window.location.replace(window.location.href)">
	</form>
	<%
	ListIterator<Long> question_id_iter = question_ids.listIterator();
	ListIterator<String> question_iter = questions.listIterator();
	while (question_iter.hasNext()) {
		long question_id = (long) question_id_iter.next();
		String question = (String) question_iter.next();
	%>
		<%=question_id %>: <%=question %> <br>
	<%
	}
	%>
</body>
</html>