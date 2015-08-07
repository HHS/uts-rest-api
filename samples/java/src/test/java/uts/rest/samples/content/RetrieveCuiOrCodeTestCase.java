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

/*This example allows you to retrieve CUI or source-asserted identifier information
Examples are at https://github.com/jayway/rest-assured/tree/master/examples/rest-assured-itest-java/src/test/java/com/jayway/restassured/itest/java
For convenience, google's quick json parser is also included in the pom.xml file:
https://code.google.com/p/quick-json/

You can run this class as a Junit4 test case - be sure and put each of the arguments as VM arguments 
in your runtime configuration, such as -Dusername=username -Dpassword=password -Did=C0018787

*/

public class RetrieveCuiOrCodeTestCase {

    
	String username = System.getProperty("username"); 
	String password = System.getProperty("password");
	String id = System.getProperty("id");
	//source,version are not required arguments
	String source = System.getProperty("source");
	String version = System.getProperty("version");
	RestTicketClient ticketClient = new RestTicketClient(username,password);
	//get a ticket granting ticket for this session.
	String tgt = ticketClient.getTgt();

	@Test
	public void RetrieveCuiOrCode() throws Exception {
		
		    version = System.getProperty("version") == null ? "current": System.getProperty("version");
			//if you do not specify a source vocabulary, the script assumes you're searching for CUI
		    String path = System.getProperty("source") == null ? "/rest/content/"+version+"/CUI/"+id: "/rest/content/"+version+"/source/"+source+"/"+id;
			HashMap<String,Object> results = new HashMap<String,Object>();
	    	
			RestAssured.baseURI = "https://uts-ws.nlm.nih.gov";
	    	Response response =  given()//.log().all()
	                .request().with()
	                	.param("ticket", ticketClient.getST(tgt))
	        	 .expect()
	       		 .statusCode(200)
	        	 .when().get(path);
	        	 //response.then().log().all();;
            
	    	results = with(response.getBody().asInputStream()).get("result");
	    	
	    		for(String k: results.keySet()) {
	    			/*print out every field in the JSON.  Full list of fields returned is available at:
	    			https://documentation.uts.nlm.nih.gov/rest/concept/index.html and
	    			https://documentation.uts.nlm.nih.gov/rest/source-asserted-identifiers/index.html
	    			*/
	    			System.out.println(k+": "+ results.get(k));
	    		}

	}
}
