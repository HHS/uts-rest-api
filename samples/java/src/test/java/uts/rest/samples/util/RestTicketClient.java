package uts.rest.samples.util;
import static com.jayway.restassured.RestAssured.given;
import com.jayway.restassured.RestAssured;
import com.jayway.restassured.response.Headers;
import com.jayway.restassured.response.Response;

public class RestTicketClient {
	
	private String tgt;
	private String st;
	private String service = "http://umlsks.nlm.nih.gov";
	private String username = null;
	private String password = null;
	private String authUri = "https://utslogin.nlm.nih.gov";
	
	public RestTicketClient (String username, String password) {
		
		this.username = username;
		this.password = password;
	}

	public String getTgt()
	{
		RestAssured.baseURI=authUri;
    	Response response =  given()//.log().all()
            .request().with()
            	.param("username", username)
            	.param("password", password)
    		.expect()
   				.statusCode(201)
    	.when().post("/cas/v1/tickets");
    	
    	Headers h = response.getHeaders();
    	String tgt = h.getValue("location").substring(h.getValue("location").indexOf("TGT"));
    	//response.then().log()
    	return tgt;
	}
	
	public String getST(String tgt)
	{
		RestAssured.baseURI=authUri;
    	Response response =  given()//.log().all()
            .request().with()
            	.param("service", service)
    		.expect()
   				.statusCode(200)
    	.when().post("/cas/v1/tickets/" + tgt);
    	
    	String st = response.getBody().asString();
    	//response.then().log().all();
    	return st;		
	}
	
	public void logout(String ticket)
	{
		RestAssured.baseURI=authUri;
    	Response response =  given()//.log().all()
            .request().with()
            	.param("service", service)
    		.expect()
   				.statusCode(200)
    	.when().delete("/cas/v1/tickets/" + ticket);	
    //	response.then().log().all();
	}


	
		

}
