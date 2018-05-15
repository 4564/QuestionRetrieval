<%@page import="java.util.LinkedList"%>
<%@page import="java.util.ListIterator"%>
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
<script type="text/javascript">
function judge(){
	var candidate_ids=document.getElementsByName('candidate_id');
	for (var i = 0; i < candidate_ids.length; ++i) {
		var status = false;
 		var _radObj=document.getElementsByName(candidate_ids[i].value);
	 	for(var j = 0; j < _radObj.length; ++j){
			if(_radObj[j].checked){
				status = true;
			}
		}
		if(! status){
			alert('还有的没判断，请仔细检查！');
			return false
		}
	}
	return true;
}
</script>
<title>标记数据</title>
</head>
<body>
	<%
	// 初始化数据库连接
	String configPath = pageContext.getServletContext().getRealPath("/config.properties");
	HashMap<String, String> parameters = PropertyTool.getProperties(configPath);
	String url = String.format(
			"jdbc:mysql://%s:%s/%s?useUnicode=true&autoReconnect=true&rewriteBatchedStatements=true",
			parameters.get("host"), parameters.get("port"), parameters.get("database"));
	DBTool dbTool = new DBTool(url, parameters.get("user"), parameters.get("password"));

	// flag这个参数是必须的，默认为 1
	int flag = 1;
	String flag_str = request.getParameter("flag");
	if (flag_str != null)
		flag = Integer.parseInt(flag_str);
	
	// 处理有更新的情况
	String query_id_str = request.getParameter("query_id");
	if (query_id_str != null){
		long query_id = Long.parseLong(query_id_str);
		String[] candidate_id_strs = request.getParameterValues("candidate_id");
		List<Long> candidate_ids = new LinkedList<Long>();
		for (String candidate_id_str : candidate_id_strs) {
			candidate_ids.add(Long.parseLong(candidate_id_str));
		}
		// 这里要搜集原flag跟relevance
		List<Integer> candidate_flags = dbTool.getFlags(query_id, candidate_ids);
		List<Integer> candidate_relevance = dbTool.getRelevance(query_id, candidate_ids);
		
		ListIterator<Long> candidate_id_iter = candidate_ids.listIterator();
		ListIterator<Integer> candidate_flag_iter = candidate_flags.listIterator();
		ListIterator<Integer> candidate_relevance_iter = candidate_relevance.listIterator();
		while (candidate_id_iter.hasNext()) {
			long candidate_id = (long) candidate_id_iter.next();
			int old_flag = (int) candidate_flag_iter.next();
			int old_relevance = (int) candidate_relevance_iter.next();
			int relevance = Integer.parseInt(request.getParameter(candidate_id + ""));
			// 这里就不能简单的插入了要看 其原来的情况
			if (flag == 3) {
				// 二选一，直接确定
				dbTool.update_relevance(query_id, candidate_id, relevance, 4);				
			} else if (old_flag == -1){
				// 没人标过，直接赋值
				dbTool.update_relevance(query_id, candidate_id, relevance, flag);				
			} else if (relevance == old_relevance){
				// 与原结果一样就不用再标了
				dbTool.update_relevance(query_id, candidate_id, relevance, 4);
			} else {
				// 1号，2号不统一，要找3号
				if (flag == 1) {
					relevance = old_relevance * 10 + relevance;
				} else {
					relevance = relevance * 10 + old_relevance;
				}
				dbTool.update_relevance(query_id, candidate_id, relevance, 3);	
			}
			
		}
	}
	// 随机抽象要标记的查询
	long query_id = dbTool.getUnmarkQueryID(flag);
	if (query_id == -1 ) {// 都标记完了
	%>
		数据已标记完成！flag=<%=flag %>	
	<%
		dbTool.close();
		return;
	}
	String query = dbTool.getQuestionByQuestionID(query_id);
	List<Long> candidate_ids = dbTool.getMarkCandidateIDs(query_id);
	List<String> candidates = dbTool.getQuestionsByQuestionIDs(candidate_ids);
	List<Integer> candidate_flags = dbTool.getFlags(query_id, candidate_ids);
	List<Integer> candidate_relevance = dbTool.getRelevance(query_id, candidate_ids);
	dbTool.close();
	%>
	相关性标记:flag=<%=flag %><br>
	查询-><%=query_id %>: <%=query %><br>
	<form action="mark.jsp" onsubmit="return judge()" method="post">
		<input name="query_id" type="hidden" value=<%=query_id %>> 
		<input name="flag" type="hidden" value=<%=flag %>>
		<%
		ListIterator<Long> candidate_id_iter = candidate_ids.listIterator();
		ListIterator<String> candidate_iter = candidates.listIterator();
		ListIterator<Integer> candidate_flag_iter = candidate_flags.listIterator();
		ListIterator<Integer> candidate_relevance_iter = candidate_relevance.listIterator();
		while (candidate_iter.hasNext()) {
			long candidate_id = (long) candidate_id_iter.next();
			int candidate_flag = (int) candidate_flag_iter.next();
			int relevance = (int) candidate_relevance_iter.next();
			String candidate = (String) candidate_iter.next();
			if (flag == 3 ) {
				// 第三方进行判断，只要管candidate_flag ==3 跟4 
				if (candidate_flag == 3) {
					int relevance1 = relevance % 10;
					int relevance2 = relevance / 10;
				%>
					<input name="candidate_id" type="hidden" value=<%=candidate_id%> />
					<input name=<%=candidate_id %> type="radio" value=0 <%if (0 != relevance1 && 0 != relevance2) {%>disabled="disabled"<%}%>/>差&nbsp;
					<input name=<%=candidate_id %> type="radio" value=1 <%if (1 != relevance1 && 1 != relevance2) {%>disabled="disabled"<%}%>/>一般
					<input name=<%=candidate_id %> type="radio" value=2 <%if (2 != relevance1 && 2 != relevance2) {%>disabled="disabled"<%}%>/>好&nbsp; 
					<label><%=candidate_id %>:<%=candidate %></label><br>		
				<%
				} else if (candidate_flag == 4) {
				%>
					<input name=<%=candidate_id %> type="radio" value=0 disabled="disabled" <%if (0 == relevance) {%>checked="checked"<%}%>/>差&nbsp;
					<input name=<%=candidate_id %> type="radio" value=1 disabled="disabled" <%if (1 == relevance) {%>checked="checked"<%}%>/>一般
					<input name=<%=candidate_id %> type="radio" value=2 disabled="disabled" <%if (2 == relevance) {%>checked="checked"<%}%>/>好&nbsp; 
					<label><%=candidate_id %>:<%=candidate %></label><br>		
				<%
				}
			} else if (candidate_flag == flag || candidate_flag == 3 || candidate_flag == 4){
				// 已经标记过了，不用标记
				if (candidate_flag == 3){
					if (flag == 1)
						relevance = relevance % 10;
					else if (flag == 2)
						relevance = relevance / 10;
				}
			%>
				<input name=<%=candidate_id %> type="radio" value=0 disabled="disabled" <%if (0 == relevance) {%>checked="checked"<%}%>/>差&nbsp;
				<input name=<%=candidate_id %> type="radio" value=1 disabled="disabled" <%if (1 == relevance) {%>checked="checked"<%}%>/>一般
				<input name=<%=candidate_id %> type="radio" value=2 disabled="disabled" <%if (2 == relevance) {%>checked="checked"<%}%>/>好&nbsp; 
				<label><%=candidate_id %>:<%=candidate %></label><br>		
			<%
			} else {
				// 没有标记过的要标记
			%>
				<input name="candidate_id" type="hidden" value=<%=candidate_id%> />
				<input name=<%=candidate_id %> type="radio" value=0/>差&nbsp;
				<input name=<%=candidate_id %> type="radio" value=1/>一般
				<input name=<%=candidate_id %> type="radio" value=2/>好&nbsp; 
				<label><%=candidate_id %>:<%=candidate %></label><br>
		 	
			<%
			}
		}
		%>
		<input type="submit" value="提交" /> <%-- 弄一个是否全都选了的JS检测 --%>
	</form>	

</body>
</html>