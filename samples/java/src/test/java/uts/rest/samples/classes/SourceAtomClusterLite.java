package uts.rest.samples.classes;

import java.util.HashMap;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties({"classType"})

public class SourceAtomClusterLite {

	
	private String ui;
	private String name;
	private boolean obsolete;
	private boolean suppressible;
	private String rootSource;
	private int cVMemberCount;
	private int atomCount;
	private String concepts;
	private String atoms;
	private String parents;
	private String children;
    private String descendants;
    private String ancestors;
	private String relations;
	private String definitions;
	private String attributes;
	private String defaultPreferredAtom;
	private List<HashMap<String,Object>> subsetMemberships;
	private List<HashMap<String,Object>> contentViewMemberships;
	
	
	public String getUi() {
		
		return this.ui;
	}
	
	public String getName() {
		
		return this.name;
	}
	
	public boolean getObsolete() {
		
		return this.obsolete;
	}
	
	public boolean getSuppressible() {
		
		return this.suppressible;
	}
	
	public String getAtoms() {
		
		return this.atoms;
	}
	
	public String getConcepts() {
		
		return this.concepts;
	}

	public String getRootSource() {
		
		return this.rootSource;
	}
	
	public int getAtomCount() {
		
		return this.atomCount;
	}
	
	public int getCVMemberCount() {
		
		return this.cVMemberCount;
	}
     
	public String getParents() {
		
		return this.parents;
	}

	public String getChildren() {
		
		return this.children;
	}
	
	public String getAncestors() {
		
		return this.ancestors;
		
	}
	
	public String getDescendants() {
		
		return this.descendants;
	}
	
	public String getDefinitions() {
		
		return this.definitions;
	}
	
	public String getRelations() {
		
		return this.relations;
	}
	
	public String getAttributes() {
		
		return this.attributes;
	}
	
	public String getDefaultPreferredAtom() {
		
		return this.defaultPreferredAtom;
	}
	
	private List<HashMap<String,Object>> getSubsetMemberships() {
		
		return this.subsetMemberships;
	}
	
    private List<HashMap<String,Object>> getContentViewMemberships() {
		
		return this.contentViewMemberships;
	}
	
	private void setAtoms(String atoms) {
		
		this.atoms = atoms;
	}
	
	private void setAtomCount(int atomCount) {
		
		this.atomCount = atomCount;
	}
	
	private void setcVMemberCount(int cVMemberCount) {
		
		this.cVMemberCount = cVMemberCount;
	}
	
	private void setUi(String ui) {
		
		this.ui = ui;
	}
	
	private void setConcepts(String concepts) {
		
		this.concepts = concepts;
	}
	
	private void setName(String name){
		
		this.name=name;
	}
	
	private void setRootSource(String rootSource) {
		
		this.rootSource = rootSource;
	}
	
	private void setObsolete(boolean obsolete) {
		
		this.obsolete = obsolete;
	}
	
	private void setSuppressible(boolean suppressible) {
		
		this.suppressible = suppressible;
	}
	
	private void setDefinitions (String definitions) {
		
		this.definitions = definitions;
	}
	
	private void setRelations (String relations) {
		
		this.relations = relations;
	}
	
	private void setChildren(String children) {
		
		this.children = children;
	}
	
	
	private void setParents(String parents) {
		
		this.parents = parents;
	}
	
	private void setAncestors(String ancestors)  {
		
		this.ancestors = ancestors;
	}
	
	private void setAttributes(String attributes) {
		
		this.attributes = attributes;
		
	}
	
	private void setDefaultPreferredAtom(String defaultPreferredAtom) {
		
		this.defaultPreferredAtom = defaultPreferredAtom;
	}
	
	private void setContentViewMemberships(List<HashMap<String,Object>> contentViewMemberships) {
		
		this.contentViewMemberships = contentViewMemberships;
		
	}
	
    private void setSubsetMemberships(List<HashMap<String,Object>> subsetMemberships) {
		
		this.subsetMemberships = subsetMemberships;
		
	}
}
