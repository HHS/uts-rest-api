package uts.rest.samples.search;
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

/*This example allows you to search terms in the UMLS
Examples are at https://github.com/jayway/rest-assured/tree/master/examples/rest-assured-itest-java/src/test/java/com/jayway/restassured/itest/java
For convenience, google's quick json parser is also included in the pom.xml file:
https://code.google.com/p/quick-json/
You can run this class as a Junit4 test case - be sure and put each of the 4 arguments as VM arguemnts
The test will fail once the result set reads 'NO RESUTLS'.  Improved paging will take care of this 
in the near future. 
in your runtime configuration, such as -Dusername=username -Dpassword=password -Dterm = "diabetic foot"

*/

public class SearchTermsTestCase {

	String username = System.getProperty("username"); 
	String password = System.getProperty("password");
	//version is not a required argument - if left out you will search against the latest UMLS publication
	String version = System.getProperty("version");
	String term = System.getProperty("term");
	RestTicketClient ticketClient = new RestTicketClient(username,password);
	//get a ticket granting ticket for this session.
	String tgt = ticketClient.getTgt();
	

	@Test
	public void SearchTerm() throws Exception {
		
	version = System.getProperty("version") == null ? "current": System.getProperty("version");

		int page = 0;
		
		while(true) {
			List<HashMap<String,Object>> results = new ArrayList<HashMap<String,Object>>();
	    	RestAssured.baseURI = "https://uts-ws.nlm.nih.gov";
	    	Response response =  given()
	                .request().with()
	                	.param("ticket", ticketClient.getST(tgt))
	                	.param("string", term)
	                	.param("page",page++)
	                	//uncomment below to have results come back as SNOMED CT concept IDs
	                	//.param("returnIdType", "sourceConcept")
	                	//.param("sabs", "SNOMEDCT_US")
	        	 .expect()
	       		 .statusCode(200)
	       		 .body(not(containsString("NO RESULTS")))
	        	 .when().get("/rest/search/"+version);
	    	System.out.println("Page "+page);
	    	results = with(response.getBody().asInputStream()).get("result.results");
	        
	    	//everything returned under the /search endpoint is a json object - there are no arrays.
	    	//See http://documentation.uts.nlm.nih.gov/rest/search/index.html#sample-output for a complete list of fields output under the /search endpoint
	    	for(HashMap<String, Object>result:results) {
	    		
	    		for(String k: result.keySet()) {
	    			
	    			System.out.println(k+": "+ result.get(k));
	    		}
	    		System.out.println("**");
	    	}
	    	System.out.println("----------");
		}
	
	
		
	}
}
