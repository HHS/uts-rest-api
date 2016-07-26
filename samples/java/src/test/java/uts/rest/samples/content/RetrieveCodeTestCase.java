/*This example allows you to retrieve information about a known source-asserted identifier.
You can run this class as a Junit4 test case - be sure and put each of the arguments as VM arguments 
in your runtime configuration, such as -Dapikey -Did=9468002 -Dsource=SNOMEDCT_US
*/

package uts.rest.samples.content;
import uts.rest.samples.util.RestTicketClient;
import uts.rest.samples.classes.SourceAtomClusterLite;

import org.junit.Test;

import com.jayway.jsonpath.Configuration;
import com.jayway.jsonpath.JsonPath;
import com.jayway.jsonpath.spi.mapper.JacksonMappingProvider;
import com.jayway.restassured.RestAssured;
import com.jayway.restassured.response.Response;

import static com.jayway.restassured.RestAssured.given;
import static org.apache.commons.lang.StringUtils.join;


public class RetrieveCodeTestCase {
  
	//String username = System.getProperty("username"); 
	//String password = System.getProperty("password");
	String apiKey = System.getProperty("apikey");
	String id = System.getProperty("id");
	String version = System.getProperty("version");
	String source = System.getProperty("source");
	RestTicketClient ticketClient = new RestTicketClient(apiKey);
	//get a ticket granting ticket for this session.
	String tgt = ticketClient.getTgt();

	@Test
	public void RetrieveCodes() throws Exception {
		
		    //if you omit the -Dversion parameter, use 'current' as the default.
		    version = System.getProperty("version") == null ? "current": System.getProperty("version");
		    String path = "/rest/content/"+version+"/source/"+source+"/"+id;	    	
			RestAssured.baseURI = "https://uts-ws.nlm.nih.gov";
	    	Response response =  given().log().all()
	                .request().with()
	                	.param("ticket", ticketClient.getST(tgt))
	        	 .expect()
	       		 .statusCode(200)
	        	 .when().get(path);
	        	 //response.then().log().all();;     
	    	String output = response.getBody().asString();
			Configuration config = Configuration.builder().mappingProvider(new JacksonMappingProvider()).build();
			SourceAtomClusterLite code = JsonPath.using(config).parse(output).read("$.result",SourceAtomClusterLite.class);
				
 			System.out.println(source+" code: " +code.getUi()+": "+code.getName());
			System.out.println("Number of Atoms: " + code.getAtomCount());
			System.out.println("Atoms: "+code.getAtoms());
			System.out.println("Relations: "+code.getRelations());
			System.out.println("Parents: "+code.getParents());
			System.out.println("Children: "+code.getChildren());
			System.out.println("Ancestors: "+code.getAncestors());
			System.out.println("Descendants: "+code.getDescendants());
			System.out.println("Highest Ranking Atom: "+code.getDefaultPreferredAtom());


	}
}
