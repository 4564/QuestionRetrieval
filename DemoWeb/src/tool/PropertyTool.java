package tool;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Properties;

// 处理配置文件
public class PropertyTool {
	// 读取读取配置文件，返回对应HashMap
	public static HashMap<String, String> getProperties(String path) {
		HashMap<String, String> result = new HashMap<>();
		Properties prop = new Properties();
		try { 
			InputStream in = new BufferedInputStream(new FileInputStream(path));
			prop.load(in); 
			// 遍历
			Iterator<String> it = prop.stringPropertyNames().iterator(); 
			while (it.hasNext()) {
				String key = it.next();
				result.put(key, prop.getProperty(key)); // 存入
			}
			in.close();
		} catch (Exception e) {
			System.out.println(e);
		}
		return result;
	}
	
	// 修改对应配置文件，改为指定的
	public static void setProprety(String path, String key, String value) {
		Properties prop = new Properties();
		try { 
			InputStream in = new BufferedInputStream(new FileInputStream(path));
			prop.load(in); // 加载
			String oldValue = prop.getProperty(key); 
			prop.setProperty(key, value); // 更新
			FileOutputStream out = new FileOutputStream(path); // 写入
			prop.store(out, key + " = " + oldValue + " Update On");
			out.close();
			in.close();
		} catch (Exception e) {
			System.out.println(e);
		}
	}
}
