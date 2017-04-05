/*This example allows you to retrieve atoms for a known CUI or source-asserted identifier in the UMLS
You can run this class as a Junit4 test case - be sure and put each of the arguments as VM arguments
in your runtime configuration, such as -Dapikey -Did=C0155502.
To retrieve atoms that belong to a source-asserted concept, descriptor, or code, use the 
-Dsource parameter, such as -Dsource=SNOMEDCT_US
*/
package uts.rest.samples.content;
import uts.rest.samples.classes.AtomLite;
import uts.rest.samples.util.RestTicketClient;

import org.junit.Test;

import com.jayway.jsonpath.Configuration;
import com.jayway.jsonpath.JsonPath;
import com.jayway.jsonpath.spi.mapper.JacksonMappingProvider;
import com.jayway.restassured.RestAssured;
import com.jayway.restassured.response.Response;

import static com.jayway.restassured.RestAssured.given;
import static org.junit.Assert.*;


public class RetrieveAtomsTestCase {
	
	//String username = System.getProperty("username"); 
	//String password = System.getProperty("password");
	String apiKey = System.getProperty("apikey");
	String id = System.getProperty("id");
	String source = System.getProperty("source");
	//specifying version is not required - if you leave it out the script will default to the latest UMLS publication.
	String version = System.getProperty("version");
	RestTicketClient ticketClient = new RestTicketClient(apiKey);
	//get a ticket granting ticket for this session.
	String tgt = ticketClient.getTgt();
	
	@Test
	public void RetrieveAtoms() throws Exception {
		
		    version = System.getProperty("version") == null ? "current": System.getProperty("version");
			//if you do not specify a source vocabulary, the script assumes you're searching for CUI
		    String path = System.getProperty("source") == null ? "/rest/content/"+version+"/CUI/"+id+"/atoms" : "/rest/content/"+version+"/source/"+source+"/"+id+"/atoms";
		    AtomLite[] atoms;
		    int page = 1;
		    int pageCount;
		    int numberOfAtoms = 0;
		    //UMLS CUI may have hundreds of atoms, so we've set up a way to page through them here.
		    do {
		    
		    System.out.println("Page "+page);
		    System.out.println("***********");
			RestAssured.baseURI = "https://uts-ws.nlm.nih.gov";
	    	Response response =  given()//.log().all()
	                .request().with()
	                //we need a new service ticket for each call since we're requesting multiple pages.
	                	.param("ticket", ticketClient.getST(tgt))
	                	//.param("language", "ENG")
	                	//.param("ttys","PT")
	                	//.param("sabs","SNOMEDCT_US")
	                	.param("pageNumber",page)
	        	 .expect()
	       		 .statusCode(200)
	        	 .when().get(path);
	        	 //response.then().log().all();;

	    	String output = response.getBody().asString();
			Configuration config = Configuration.builder().mappingProvider(new JacksonMappingProvider()).build();
			pageCount = JsonPath.using(config).parse(output).read("$.pageCount");
			atoms = JsonPath.using(config).parse(output).read("$.result",AtomLite[].class);
			
			for(AtomLite atom:atoms) {
				
			   System.out.println("AUI: "+ atom.getUi());
			   System.out.println("Name: " + atom.getName());
			   System.out.println("Term Type: " + atom.getTermType());
			   System.out.println("Obsolete: " + atom.getObsolete());
			   System.out.println("Vocabulary: " + atom.getRootSource());
			   System.out.println("UMLS Concept: " + atom.getConcept());
			   System.out.println("Source Concept: " + atom.getSourceConcept());
			   System.out.println("Source Descriptor: " + atom.getSourceDescriptor());
			   System.out.println("Source Code: " + atom.getCode());
			   System.out.println("-------");
			}
            
            numberOfAtoms += atoms.length;
            page++;
            
            assertTrue(atoms.length > 0);
		    
		   } 
		    
		    while(page <= pageCount );

		    System.out.println("Retrieved " + numberOfAtoms  +" atoms for " + id);
	}
	

}
