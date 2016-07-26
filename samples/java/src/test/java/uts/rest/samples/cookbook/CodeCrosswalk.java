/*This example loads a file of hpo identifiers(hpo-codes.txt from the 'resources' folder)
 * and retrieves SNOMED CT preferred terms 
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

public class CodeCrosswalk {

	//String username = System.getProperty("username"); 
	//String password = System.getProperty("password");
	String apiKey = System.getProperty("apikey");
	String version = System.getProperty("version");
	RestTicketClient ticketClient = new RestTicketClient(apiKey);
	//get a ticket granting ticket for this session.
	String tgt = ticketClient.getTgt();
	SourceAtomClusterLite[] sourceAtomClusters;
	
	@Test
	public void RunCrosswalk() throws Exception {
		
	   version = System.getProperty("version") == null ? "current": System.getProperty("version");
	   System.out.println("HPO Id|SNOMEDCT ConceptId|SNOMEDCT Name");
	   try (BufferedReader br = new BufferedReader(new FileReader("resources/hpo-codes.txt"))) {
	   String hpo;
	   
	    while ((hpo = br.readLine()) != null) {

	    	try  {
	    		sourceAtomClusters = CrossWalkCodes(hpo, "SNOMEDCT_US");
	    		for (SourceAtomClusterLite sourceAtomCluster:sourceAtomClusters) {
	    			
	    			System.out.println(hpo+"|"+sourceAtomCluster.getUi()+"|"+ sourceAtomCluster.getName());
	    			
	    		}
	    		
	    	}
	    	catch (Exception ex) {
	    		//cannot find a CUI-based match to SNOMED CT
	    		System.out.println(hpo + "||");
	    		
	    	}
	      
	    }
   
	  }	
}

	
public SourceAtomClusterLite[] CrossWalkCodes(String code, String targetSource) {
	    RestAssured.baseURI = "https://uts-ws.nlm.nih.gov";
	    String path = "/rest/crosswalk/"+version+"/source/HPO/"+code;
	    
		Response response =  given()//.log().all()
				.request().with()
				.param("ticket", ticketClient.getST(tgt))
				.param("targetSource", "SNOMEDCT_US")
				.when().get(path);
		
		String output = response.getBody().asString();
		Configuration config = Configuration.builder().mappingProvider(new JacksonMappingProvider()).build();
		sourceAtomClusters = JsonPath.using(config).parse(output).read("$.result",SourceAtomClusterLite[].class);
	    return sourceAtomClusters;
    
    }
	
}


