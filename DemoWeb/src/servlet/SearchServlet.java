package servlet;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.List;
import java.util.ListIterator;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import tool.DBTool;
import tool.PropertyTool;
import lucene.LuceneReader;

/**
 * Servlet implementation class SearchServlet
 */
@WebServlet(description = "deal search request", urlPatterns = { "/SearchServlet" })
public class SearchServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public SearchServlet() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {		
		String configPath = getServletContext().getRealPath("config.properties");
		HashMap<String, String> config = PropertyTool.getProperties(configPath);
		
		request.setCharacterEncoding("utf-8");
		String q = request.getParameter("query");
		
		List<Long> question_ids = null;
		try (LuceneReader reader = new LuceneReader(config.get("index_path"), config.get("data_path"))){
			question_ids = reader.searchQuestions(q, 10);
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		response.setContentType("text/html;charset=utf-8");
		String url = String.format(
				"jdbc:mysql://%s:%s/%s?useUnicode=true&autoReconnect=true&rewriteBatchedStatements=true",
				config.get("host"), config.get("port"), config.get("database"));
		try (PrintWriter out = response.getWriter();
				DBTool dbTool = new DBTool(url, config.get("user"), config.get("password"));){
			out.println(q);
			List<String> questions = dbTool.getQuestionsByQuestionIDs(question_ids);
			assert question_ids.size() == questions.size();
			
			ListIterator<Long> iter_question_ids = question_ids.listIterator();
			ListIterator<String> iter_questions = questions.listIterator();
			while (iter_question_ids.hasNext()) {
				out.println("<br>" + String.format("%d:%s", 
						(long) iter_question_ids.next(), (String) iter_questions.next()));
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		doGet(request, response);
	}

}
