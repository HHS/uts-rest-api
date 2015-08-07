/*This example allows you to retrieve atoms for a known CUI in the UMLS
Examples are at https://github.com/jayway/rest-assured/tree/master/examples/rest-assured-itest-java/src/test/java/com/jayway/restassured/itest/java
For convenience, google's quick json parser is also included in the pom.xml file:
https://code.google.com/p/quick-json/
You can run this class as a Junit4 test case - be sure and put each of the arguments as VM arguments
The test will fail once the final page of results is rendered - this will be fixed with improved paging in the near future.
in the near future. 
in your runtime configuration, such as -Dusername=username -Dpassword=password -Did=C0155502

*/
package uts.rest.samples.content;
import uts.rest.samples.util.RestTicketClient;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import org.junit.Test;
import static org.hamcrest.Matchers.*;
import com.jayway.restassured.RestAssured;
import com.jayway.restassured.response.Response;
import static com.jayway.restassured.RestAssured.given;
import static com.jayway.restassured.path.json.JsonPath.with;
import org.apache.log4j.Logger;

public class RetrieveAtomsTestCase {
	
	String username = System.getProperty("username"); 
	String password = System.getProperty("password");
	String id = System.getProperty("id");
	//specifying version is not required - if you leave it out the script will default to the latest UMLS publication.
	String version = System.getProperty("version");
	RestTicketClient ticketClient = new RestTicketClient(username,password);
	//get a ticket granting ticket for this session.
	String tgt = ticketClient.getTgt();
	
	@Test
	public void RetrieveAtoms() throws Exception {
		
		    version = System.getProperty("version") == null ? "current": System.getProperty("version");
			//if you do not specify a source vocabulary, the script assumes you're searching for CUI
		    String path = "/rest/content/"+version+"/CUI/"+id+"/atoms";
		    List<HashMap<String,Object>> results = new ArrayList<HashMap<String,Object>>();
		    int page=1;
		    do {
		    System.out.println("Page "+page);
			RestAssured.baseURI = "https://uts-ws.nlm.nih.gov";
	    	Response response =  given()//.log().all()
	                .request().with()
	                	.param("ticket", ticketClient.getST(tgt))
	                	.param("language", "ENG")
	                	//.param("ttys","PT")
	                	//.param("sabs","SNOMEDCT_US,ICD9CM")
	                	.param("page",page++)
	        	 .expect()
	       		 .statusCode(200)
	        	 .when().get(path);
	        	 //response.then().log().all();;

	    	results = with(response.getBody().asInputStream()).get("result");
	    	
            for(HashMap<String, Object>result:results) {
	    		
	    		for(String k: result.keySet()) {
	    			
	    			System.out.println(k+": "+ result.get(k));
	    		}
	    		//System.out.println("**");
	    	}
           
            System.out.println("----------");
		 }while(results.size() > 0);
	}

}
