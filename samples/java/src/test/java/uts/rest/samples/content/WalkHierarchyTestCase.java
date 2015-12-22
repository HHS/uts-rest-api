package uts.rest.samples.content;
import uts.rest.samples.classes.SourceAtomClusterLite;
import uts.rest.samples.util.RestTicketClient;
import org.junit.Test;
import com.jayway.jsonpath.Configuration;
import com.jayway.jsonpath.JsonPath;
import com.jayway.jsonpath.spi.mapper.JacksonMappingProvider;
import com.jayway.restassured.RestAssured;
import com.jayway.restassured.response.Response;
import static com.jayway.restassured.RestAssured.given;
import static org.junit.Assert.*;

public class WalkHierarchyTestCase {

	String username = System.getProperty("username"); 
	String password = System.getProperty("password");
	String id = System.getProperty("id");
	String source = System.getProperty("source");
	//specifying version is not required - if you leave it out the script will default to the latest UMLS publication.
	String version = System.getProperty("version");
	//use either 'parents', 'children', 'ancestors', or 'descendants' here
	String operation = System.getProperty("operation");
	RestTicketClient ticketClient = new RestTicketClient(username,password);
	//get a ticket granting ticket for this session.
	String tgt = ticketClient.getTgt();
	
	@Test
	public void WalkHierarchy() throws Exception {
		
	    version = System.getProperty("version") == null ? "current": System.getProperty("version");
		//if you do not specify a source vocabulary, the script assumes you're searching for CUI
	    String path = "/rest/content/"+version+"/source/"+source+"/"+id+"/"+operation;
	    SourceAtomClusterLite[] sourceAtomClusters;
	    int page=1;
	    int results = 0;
	    int pageCount;
	    //calls to descendants may produce several hundred or even several thousand results.
	    //so we page through them here.  
	    do {
		    System.out.println("Page "+page);
		    System.out.println("***********");
			RestAssured.baseURI = "https://uts-ws.nlm.nih.gov";
	    	Response response =  given()//.log().all()
	                .request().with()
	                //we need a new service ticket for each call since we're requesting multiple pages.
	                	.param("ticket", ticketClient.getST(tgt))
	                	.param("pageNumber",page)
	        	 .expect()
	       		 .statusCode(200)
	        	 .when().get(path);
	        	 //response.then().log().all();;

	    	String output = response.getBody().asString();
			Configuration config = Configuration.builder().mappingProvider(new JacksonMappingProvider()).build();
			pageCount = JsonPath.using(config).parse(output).read("$.pageCount");
			sourceAtomClusters = JsonPath.using(config).parse(output).read("$.result",SourceAtomClusterLite[].class);
	    	
			for(SourceAtomClusterLite sourceAtomCluster:sourceAtomClusters) {
				
				System.out.println("Ui: "+sourceAtomCluster.getUi());
				System.out.println("Name: "+sourceAtomCluster.getName());
				System.out.println("Number of Atoms: "+sourceAtomCluster.getAtomCount());
				System.out.println("Concepts: "+sourceAtomCluster.getConcepts());
				System.out.println("Ancestors: "+sourceAtomCluster.getAncestors());
				System.out.println("Parents: "+ sourceAtomCluster.getParents());
				System.out.println("Children: "+sourceAtomCluster.getChildren());
				System.out.println("Descendants: "+sourceAtomCluster.getDescendants());
				System.out.println("Highest Ranking Atom: "+sourceAtomCluster.getDefaultPreferredAtom());

			   System.out.println("-------");
			}
            
            page++;
            results += sourceAtomClusters.length;
            assertTrue(sourceAtomClusters.length > 0);
		 
		   } while(page <= pageCount );
	    System.out.println("Found " + results + " results");

	}
	    	
}
	
