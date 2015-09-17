package uts.rest.samples.search;
import uts.rest.samples.util.RestTicketClient;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import org.junit.Test;
import com.jayway.jsonpath.Configuration;
import com.jayway.jsonpath.JsonPath;
import com.jayway.restassured.RestAssured;
import com.jayway.restassured.response.Response;
import com.jayway.jsonpath.Configuration;
import com.jayway.jsonpath.spi.mapper.JacksonMappingProvider;
import static com.jayway.restassured.RestAssured.given;
import static com.jayway.restassured.path.json.JsonPath.with;
import static com.jayway.jsonpath.JsonPath.read;

/*This example allows you to search terms in the UMLS
Examples are at https://github.com/jayway/rest-assured/tree/master/examples/rest-assured-itest-java/src/test/java/com/jayway/restassured/itest/java
For convenience, google's quick json parser is also included in the pom.xml file:
https://code.google.com/p/quick-json/
You can run this class as a Junit4 test case - be sure and put each of the arguments as VM arguments
You may page through results returned from the /search endpoint until you reach the null  'ui:NONE' or 'name:NO RESULTS'.  These results will always be a single result on their own page.
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

		
		List<HashMap<String,Object>> results;
		
		int total = 0;
		int pageNumber = 0;
		do  {
			pageNumber++;
			System.out.println("Fetching results for page "+pageNumber);
	    	RestAssured.baseURI = "https://uts-ws.nlm.nih.gov";
	    	Response response =  given()//.log().all()
	                .request().with()
	                	.param("ticket", ticketClient.getST(tgt))
	                	.param("string", term)
	                	.param("pageNumber",pageNumber)
	                	//uncomment below to have results come back as SNOMED CT concept IDs
	                	//.param("returnIdType", "sourceConcept")
	                	//.param("sabs", "SNOMEDCT_US")
	                	//.param("searchType","exact") //valid values are exact,words, approximate,leftTruncation,rightTruncation, and normalizedString
	        	 .expect()
	       		 .statusCode(200)
	        	 .when().get("/rest/search/"+version);
	    	
	    	String output = response.getBody().asString();
	    	Configuration conf = Configuration.defaultConfiguration(); 
	    	results = JsonPath.using(conf).parse(output).read("$.result.results");

	    	//the /search endpoint returns an array of 'result' objects
	    	//See http://documentation.uts.nlm.nih.gov/rest/search/index.html#sample-output for a complete list of fields output under the /search endpoint
	    	for(HashMap<String, Object>result:results) {
	    		
	    		for(String k: result.keySet()) {
	    			
	    			System.out.println(k+": "+ result.get(k));
	    		}
	    		System.out.println("**");
	    	}
	    	System.out.println("----------");
	    	total += results.size();
		}while(!results.get(0).containsValue("NO RESULTS"));
		//account for the one 'NO RESULTS' result :-/
		total--;
		System.out.println("Found " + total+ " results for "+ term);
		
	
	
		
	}
}
