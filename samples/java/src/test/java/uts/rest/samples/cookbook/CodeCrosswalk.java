/*This example loads a file of hpo identifiers(hpo-codes.txt from the 'resources' folder)
 * and retrieves SNOMED CT preferred terms (or synonyms if there are no preferred term but a synonym is present) 
 * that live in the same UMLS CUI as the HPO identifier.
 */
package uts.rest.samples.cookbook;
import java.io.BufferedReader;
import java.io.FileReader;
import uts.rest.samples.util.RestTicketClient;
import uts.rest.samples.classes.*;
import org.junit.Test;
import com.jayway.jsonpath.Configuration;
import com.jayway.jsonpath.JsonPath;
import com.jayway.jsonpath.spi.mapper.JacksonMappingProvider;
import com.jayway.restassured.RestAssured;
import com.jayway.restassured.response.Response;
import static com.jayway.restassured.RestAssured.given;
import static org.junit.Assert.assertTrue;


public class CodeCrosswalk {

	String username = System.getProperty("username"); 
	String password = System.getProperty("password");
	String version = System.getProperty("version");
	RestTicketClient ticketClient = new RestTicketClient(username,password);
	//get a ticket granting ticket for this session.
	String tgt = ticketClient.getTgt();
	
	
	@Test
	public void MapCodeToCode() throws Exception {
		
	   version = System.getProperty("version") == null ? "current": System.getProperty("version");
	   System.out.println("HPO Id|SNOMEDCT ConceptId|Term Type|SNOMEDCT Name");
	   try (BufferedReader br = new BufferedReader(new FileReader("resources/hpo-codes.txt"))) {
	   String hpo;
	   
	    while ((hpo = br.readLine()) != null) {
	    	
	    	SearchResult[] results;
	    	results = SearchId(hpo);
	    	assertTrue(results.length > 0);
	    	for (SearchResult result:results) {
	    		
	    		if(result.getUi().equals("NONE")) {
	    			System.out.println(hpo+"|HPO Code not currently in UMLS");
	    		}
	    		
	    		else {
	    		   getConceptAtoms(result.getUri(),hpo,result.getName());
	    		    
	    		}
   		  
	    	 }  
	    }
   
	  }	
}
	
public SearchResult[] SearchId(String hpo) throws Exception {
		
	version = System.getProperty("version") == null ? "current": System.getProperty("version");	
		
	        SearchResult[] results;	
	    	RestAssured.baseURI = "https://uts-ws.nlm.nih.gov";
	    	Response response =  given()//.log().all()
	                .request().with()
	                	.param("ticket", ticketClient.getST(tgt))
	                	.param("string", hpo)
	                	.param("searchType", "exact")
	                	.param("inputType", "sourceUi")
	                	.param("sabs", "HPO")
	        	 .expect()
	       		 .statusCode(200)
	        	 .when().get("/rest/search/"+version);
	    	
	    	String output = response.getBody().asString();
			Configuration config = Configuration.builder().mappingProvider(new JacksonMappingProvider()).build();
			results = JsonPath.using(config).parse(output).read("$.result.results",SearchResult[].class);
	    		
		return results;
		
}
	
public void getConceptAtoms(String uri, String hpo,String name) {
		Response response =  given()//.log().all()
				.request().with()
				.param("ticket", ticketClient.getST(tgt))
				.param("sabs","SNOMEDCT_US")
				.param("ttys","PT","SY")
				.when().get(uri+"/atoms");	

		if(response.statusCode() == 404) {
			
			System.out.println(hpo+"|NO SNOMED CT concept found for "+ name);
		}
		else {
		String output = response.getBody().asString();
		Configuration config = Configuration.builder().mappingProvider(new JacksonMappingProvider()).build();
		AtomLite[] Pts = JsonPath.using(config).parse(output).read("$.result[?(@.termType=='PT')]",AtomLite[].class);
		AtomLite[] Sys = JsonPath.using(config).parse(output).read("$.result[?(@.termType=='SY')]",AtomLite[].class);
		/*here we must account for the fact that sometimes there may be more than one SNOMED CT preferred term
		 *in a UMLS CUI, or there may be no preferred terms from SNOMED CT - only synonyms.
		 */	
		if (Pts.length >= 1) {
		    for (AtomLite atom:Pts) {
		    	getSourceConceptInfo(name,atom.getSourceConcept(),hpo,atom.getTermType());
		    }
		}
		
		else {
			
			for (AtomLite atom:Sys) {
		    	getSourceConceptInfo(name,atom.getSourceConcept(),hpo,atom.getTermType());
		    }
		}
	
		    
		}
				
}
	
public void getSourceConceptInfo(String name,String uri,String hpo,String tty) {
		
		Response response =  given()//.log().all()
				.request().with()
				.param("ticket", ticketClient.getST(tgt))
				.expect()
				.statusCode(200)
				.when().get(uri);
		
		String output = response.getBody().asString();
		Configuration config = Configuration.builder().mappingProvider(new JacksonMappingProvider()).build();
		SourceAtomClusterLite sourceAtomCluster = JsonPath.using(config).parse(output).read("$.result",SourceAtomClusterLite.class);
		System.out.println(hpo+"|"+name+"|"+sourceAtomCluster.getUi()+"|"+tty+"|"+sourceAtomCluster.getName());
	}
	
}


