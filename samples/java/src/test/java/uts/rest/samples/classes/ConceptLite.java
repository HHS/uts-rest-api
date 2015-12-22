package uts.rest.samples.classes;
import com.fasterxml.jackson.annotation.*;

//of course these are customizable
@JsonIgnoreProperties({"classType","dateAdded","majorRevisionDate","status","attributeCount","cvMemberCount","suppressible","relationCount"})

public class ConceptLite {
	
	private String ui;
	private String name;
	private String[] semanticTypes;
	private int atomCount;
	private String atoms;
	private String relations;
	private String definitions;
	private String defaultPreferredAtom;
	
	public String getUi() {
		
		return this.ui;
	}
	
	public String getName() {
		
		return this.name;
	}
	
	public String[] getSemanticTypes() {
		
		return this.semanticTypes;
	}
	
	public String getAtoms() {
		
		return this.atoms;
	}

	public int getAtomCount() {
		
		return this.atomCount;
	}
	
	public String getDefinitions() {
		
		return this.definitions;
	}
	
	public String getRelations() {
		
		return this.relations;
	}
	
	public String getDefaultPreferredAtom() {
		
		return this.defaultPreferredAtom;
	}
	
	private void setAtoms(String atoms) {
		
		this.atoms = atoms;
	}
	
	private void setUi(String ui) {
		
		this.ui = ui;
	}
	
	private void setName(String name){
		
		this.name=name;
	}
	
	private void setSemanticTypes(String[] stys) {
		
		this.semanticTypes = stys;
	}
	
	private void setDefinitions (String definitions) {
		
		this.definitions = definitions;
	}
	
	private void setRelations (String relations) {
		
		this.relations = relations;
	}
	
	private void setDefaultPreferredAtom(String defaultPreferredAtom) {
		
		this.defaultPreferredAtom = defaultPreferredAtom;
		
	}
}
