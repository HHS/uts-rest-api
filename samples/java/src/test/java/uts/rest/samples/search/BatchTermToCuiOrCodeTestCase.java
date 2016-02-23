/*This example loads a file of disease names (findings.txt from the 'resources' folder)
 * and retrieves the relevant UMLS CUI(s) or source-asserted codes
 * Use Java VM args as follows:
 * -Dusername=<username> -Dpassword=<password>
 */
package uts.rest.samples.search;
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;
import uts.rest.samples.util.RestTicketClient;
import uts.rest.samples.classes.SearchResult;
import uts.rest.samples.classes.ConceptLite;
import org.junit.Test;
import com.jayway.jsonpath.Configuration;
import com.jayway.jsonpath.JsonPath;
import com.jayway.jsonpath.spi.mapper.JacksonMappingProvider;
import com.jayway.restassured.RestAssured;
import com.jayway.restassured.response.Response;
import static com.jayway.restassured.RestAssured.given;
import static org.apache.commons.lang.StringUtils.join;

public class BatchTermToCuiOrCodeTestCase {

	String username = System.getProperty("username"); 
	String password = System.getProperty("password");
	String version = System.getProperty("version");
	RestTicketClient ticketClient = new RestTicketClient(username,password);
	//get a ticket granting ticket for this session.
	String tgt = ticketClient.getTgt();
	
	
	@Test
	public void RetrieveCuis() throws Exception {
		
	   version = System.getProperty("version") == null ? "current": System.getProperty("version");
	   try (BufferedReader br = new BufferedReader(new FileReader("resources/findings.txt"))) {
	   String line;
	   
	    while ((line = br.readLine()) != null) {
	    List<SearchResult> results = SearchTerm(line);
	    if (results.size() == 0){System.out.println("No results for "+ line);}
	    int num = 1;
	       for(SearchResult result:results) {
	    	
	    	String cui = result.getUri();
	    	String ui = result.getUi();
	    	String name = result.getName();
	    	String rsab = result.getRootSource();
	    	/*TODO: Add info to the search results object so users 
	    	 * know if the search object retrieved contains CUIs or source-asserted UIs.
	    	 * For source-asserted UIs you would not be able to execute the code below which
	    	 * retrieves the semantic type(s) for a CUI.
	    	 */
	    	ConceptLite concept = getConceptInfo(cui);
	    	String stys[] = concept.getSemanticTypes();
	    	
	    	System.out.println("\nResult "+ num);
	    	System.out.println("cui:"+ cui);
	    	System.out.println("ui: " + ui);
	    	System.out.println("name:"+ name);
	    	System.out.println("Highest ranking source of cui:" + rsab);
	    	System.out.println("Semantic Type(s): "+ join(stys,","));
	    	num++;
	       }
	       System.out.println("----------");
	       
	    }
   
	  }	
	}
	
	public List<SearchResult> SearchTerm(String term) throws Exception {
		
	version = System.getProperty("version") == null ? "current": System.getProperty("version");	
		int pageNumber = 0;
		SearchResult[] results;
		List<SearchResult> holder = new ArrayList<SearchResult>();
		do  {
			pageNumber++;
	    	RestAssured.baseURI = "https://uts-ws.nlm.nih.gov";
	    	Response response =  given()//.log().all()
	                .request().with()
	                	.param("ticket", ticketClient.getST(tgt))
	                	.param("string", term)
	                	.param("pageNumber",pageNumber)
	                	//uncomment below to return only CUIs that have at least one non-obsolete/non-suppressible atom (relevant to the searchType) from the US Edition of SNOMED CT
	                	//.param("sabs","SNOMEDCT_US")
	                	//uncomment below to return CUIs that have at least one non-obsolete/non-suppressible atom that is an exact match with the search term
	                    .param("searchType","exact") //valid values are exact,words, approximate,leftTruncation,rightTruncation, and normalizedString
	                	//uncomment below to return source-asserted identifiers (from SNOMEDCT and other UMLS vocabularies) instead of CUIs
	                	//.param("returnIdType","code")
	        	 .expect()
	       		 .statusCode(200)
	        	 .when().get("/rest/search/"+version);
	    	
	    	String output = response.getBody().asString();
			Configuration config = Configuration.builder().mappingProvider(new JacksonMappingProvider()).build();
			results = JsonPath.using(config).parse(output).read("$.result.results",SearchResult[].class);

	    	//the /search endpoint returns an array of 'result' objects
	    	//See http://documentation.uts.nlm.nih.gov/rest/search/index.html#sample-output for a complete list of fields output under the /search endpoint
	        for(SearchResult result:results) {
	        	
	        	if (!results[0].getUi().equals("NONE")){holder.add(result);}
	        }
	    		
		}while(!results[0].getUi().equals("NONE"));		
		return holder;
		
	}
	
	public ConceptLite getConceptInfo(String cui) {
		Response response =  given()//.log().all()
				.request().with()
				.param("ticket", ticketClient.getST(tgt))
				.expect()
				.statusCode(200)
				.when().get(cui);
		
		String output = response.getBody().asString();
		Configuration config = Configuration.builder().mappingProvider(new JacksonMappingProvider()).build();
		ConceptLite concept = JsonPath.using(config).parse(output).read("$.result",ConceptLite.class);
        return concept;
				
	}
}


