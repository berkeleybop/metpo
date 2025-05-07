<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:interchange="http://namesforlife.com/ns/interchange" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:exsl="http://exslt.org/common" xmlns:N4L="http://doi.org/10.1601/" xmlns:obo="http://purl.obolibrary.org/obo/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" exclude-result-prefixes="exsl" version="1.0">
    
<xsl:output method="xml" standalone="no" encoding="UTF-8" omit-xml-declaration="no" indent="yes" />
    
    <xsl:strip-space elements="*" /> 

    <xsl:output indent="yes" />    
    
    <xsl:template match="/interchange:entities">
        
    <rdf:RDF xmlns:N4L="http://doi.org/10.1601/" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:xsd="http://www.w3.org/2001/XMLSchema#">

    <owl:Ontology rdf:about="http://doi.org/10.1601/">

    <owl:imports rdf:resource="http://doi.org/10.1601/" />

    </owl:Ontology>
        
        <xsl:apply-templates select="interchange:entity"/> 
        
    </rdf:RDF>

    </xsl:template>
   
    <xsl:template match="interchange:entity">       
        
        <xsl:apply-templates select="interchange:assertion"/> 
        
    </xsl:template>
    
    <xsl:template match="interchange:assertion">        
        <xsl:apply-templates select="interchange:phenotype"/>       
        <xsl:apply-templates select="interchange:observational-data"/>        
   <!-- <xsl:apply-templates select="interchange:method"/>  - non deterministic template ? -->
        <xsl:apply-templates select="interchange:inclusion-body"/>
    </xsl:template>
    <xsl:template match="interchange:inclusion-body">
        
        <rdfs:Resource rdf:about="{concat('http://doi.org/', ../../@doi)}">
            <N4L:hasOrganismObservation rdf:resource = "{concat('http://doi.org/',../../@doi,'Observation')}"/>
        </rdfs:Resource>
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../@doi,'Observation')}">
            <rdf:type rdf:resource="http://doi.org/10.1601/OrganismObservation"/>
            <N4L:hasInclusionBodyObservation rdf:resource="{concat('http://doi.org/',../../@doi,generate-id(@inclusion-body-class))}"/>
        </rdfs:Resource>
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../@doi,generate-id(@inclusion-body-class))}">
            <rdf:type rdf:resource="{@inclusion-body-class}"/>            
        </rdfs:Resource>
   <!-- <rdfs:Resource rdf:about="{@inclusion-body-class}">
        <rdfs:subClassOf rdf:resource="http://doi.org/10.1601/InclusionBodyObservation"/>
        </rdfs:Resource>-->
    </xsl:template>
    
    <xsl:template match="interchange:phenotype">
      
        <rdfs:Resource rdf:about="{concat('http://doi.org/', ../../@doi)}">
            
            <rdf:type rdf:resource="http://doi.org/10.1601/Strain" />
            
            <N4L:hasPhenotype rdf:resource="{concat('http://doi.org/',../../@doi,'Phenotype')}"/> 
            <xsl:if test="@chemical-entity"> 
            <N4L:hasOrganismObservation rdf:resource = "{concat('http://doi.org/',../../@doi,'Observation')}"/>
            </xsl:if>
        </rdfs:Resource>
      
    <xsl:if test="@chemical-entity">
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../@doi,'Observation')}">
            <rdf:type rdf:resource="http://doi.org/10.1601/OrganismObservation"/> 
            <N4L:composedOf rdf:resource="{concat('http://doi.org/',../../@doi, generate-id(@ontology-class),generate-id(@chemical-entity))}"/>           
        </rdfs:Resource>
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../@doi, generate-id(@ontology-class),generate-id(@chemical-entity))}">
            <N4L:hasAtomicObservationPhenotype rdf:resource="{concat('http://doi.org/',../../@doi,generate-id(@chemical-entity),'Phenotype')}"/>
         <!--   <xsl:if test="@ontology-class='http://doi.org/10.1601/Susceptible'">
            <rdf:type rdf:resource="http://doi.org/10.1601/InhibitedGrowth" />   
            </xsl:if>
            <xsl:if test="@ontology-class='http://doi.org/10.1601/Resistant'">
            <rdf:type rdf:resource="http://doi.org/10.1601/UninhibitedGrowth" />
            </xsl:if> -->
            <rdf:type rdf:resource="http://doi.org/10.1601/GrowthObservation" />
            <N4L:hasSubstanceCondition rdf:resource="{concat('http://doi.org/',../../@doi,generate-id(@chemical-entity))}"/>
        </rdfs:Resource>
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../@doi,generate-id(@chemical-entity),'Phenotype')}">
            <rdf:type rdf:resource="{@ontology-class}" />    
        </rdfs:Resource>
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../@doi,generate-id(@chemical-entity))}">
            <rdf:type rdf:resource="{@chemical-entity}" />    
        </rdfs:Resource>
        
    </xsl:if>
      
    
    <rdfs:Resource rdf:about="{concat('http://doi.org/',../../@doi,'Phenotype')}">
    <rdf:type rdf:resource="{@ontology-class}"/>    
    </rdfs:Resource>
        
        
           
   </xsl:template>     
    
    <xsl:template match="interchange:observational-data">
        <xsl:apply-templates select="interchange:condition"/> 
        <xsl:apply-templates select="interchange:observation"/>
        <xsl:apply-templates select="interchange:cellular-activity"/>
    </xsl:template>

    <xsl:template match="interchange:cellular-activity">
        <rdfs:Resource rdf:about="{concat('http://doi.org/', ../../../@doi)}">   
            <rdf:type rdf:resource="http://doi.org/10.1601/Strain"/>            
            <N4L:hasCellularActivity rdf:resource = "{concat('http://doi.org/',../../../@doi, generate-id(@cellular-activity-class))}"/>
        </rdfs:Resource>
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi, generate-id(@cellular-activity-class))}">
            <rdf:type rdf:resource="{@cellular-activity-class}"/>
            <N4L:hasCellularActivityOfSubstance rdf:resource="{concat('http://doi.org/',../../../@doi,generate-id(@cellular-activity-class),generate-id(../interchange:condition/@cellular-activity-condition-type))}"/>
            <N4L:hasCellularActivityValue rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean"><xsl:value-of select="../interchange:condition/@cellular-activity-condition-value"/></N4L:hasCellularActivityValue> 
        </rdfs:Resource>
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,generate-id(@cellular-activity-class),generate-id(../interchange:condition/@cellular-activity-condition-type))}">
            <rdf:type rdf:resource="{../interchange:condition/@cellular-activity-condition-type}"/>
        </rdfs:Resource>
    </xsl:template>

    <xsl:template match="interchange:condition">

        <xsl:if test="@condition-class">

            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,generate-id(../interchange:observation/@ontology-class))}">
                <N4L:hasCondition rdf:resource="{concat('http://doi.org/',../../../@doi,generate-id(@condition-class))}"/>    
            </rdfs:Resource>
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,generate-id(@condition-class))}">
                <rdf:type rdf:resource="{@condition-class}"/>
                <xsl:if test="@condition-value">
                    <N4L:hasEnvironmentalConditionValue rdf:datatype="http://www.w3.org/2001/XMLSchema#double"><xsl:value-of select="@condition-value"/></N4L:hasEnvironmentalConditionValue>
                </xsl:if>
                <xsl:if test="@unit">
                    <N4L:hasUnit rdf:resource="{concat('http://doi.org/',../../../@doi,generate-id(@unit))}"/>
                </xsl:if>
            </rdfs:Resource>
            <xsl:if test="@unit">
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,generate-id(@unit))}">
                    <rdf:type rdf:resource="{@unit}"/>   
                </rdfs:Resource>
            </xsl:if>
        </xsl:if>

        <xsl:if test="@condition-type">
            
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,generate-id(../interchange:observation/@ontology-class))}">
                <N4L:hasSubstanceCondition rdf:resource="{concat('http://doi.org/',../../../@doi,generate-id(../interchange:observation/@ontology-class),generate-id(@condition-type), generate-id(@unit))}"/>    
            </rdfs:Resource>
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,generate-id(../interchange:observation/@ontology-class),generate-id(@condition-type),generate-id(@unit))}">
                <rdf:type rdf:resource="{@condition-type}"/>
                <xsl:if test="@condition-value">
                <N4L:hasEnvironmentalConditionValue rdf:datatype="http://www.w3.org/2001/XMLSchema#double"><xsl:value-of select="@condition-value"/></N4L:hasEnvironmentalConditionValue>
                </xsl:if>
                    <xsl:if test="@unit"> <N4L:hasUnit rdf:resource="{concat('http://doi.org/',../../../@doi,generate-id(@unit))}"/></xsl:if>
            </rdfs:Resource>
            <xsl:if test="@unit">
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,generate-id(@unit))}">
                    <rdf:type rdf:resource="{@unit}"/>   
                </rdfs:Resource>
            </xsl:if>
        </xsl:if>

    </xsl:template>
    
    <xsl:template match="interchange:observation"> 
        
        <rdfs:Resource rdf:about="{concat('http://doi.org/', ../../../@doi)}">   
            <rdf:type rdf:resource="http://doi.org/10.1601/Strain"/>            
            <N4L:hasOrganismObservation rdf:resource = "{concat('http://doi.org/',../../../@doi,'Observation')}"/>
        </rdfs:Resource>
        
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,'Observation')}">
            <rdf:type rdf:resource="http://doi.org/10.1601/OrganismObservation"/> 
            <N4L:composedOf rdf:resource="{concat('http://doi.org/',../../../@doi,generate-id(@ontology-class))}"/>           
        </rdfs:Resource> 
        
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,generate-id(@ontology-class))}">
            <rdf:type rdf:resource="{@ontology-class}"/>   
        </rdfs:Resource>
        
      
        
    </xsl:template>   
    
<!-- <xsl:template match="interchange:method">
     <rdfs:Resource> 
         <xsl:attribute name="rdf:about"> <xsl:value-of select="concat('http://doi.org/', ../../@doi,generate-id(/interchange:observational-data/interchange:observation/@ontology-class),generate-id(@method-class))"/></xsl:attribute> 
          <rdf:type><xsl:attribute name="rdf:type"> <xsl:value-of select="@method-class"/></xsl:attribute> </rdf:type>
         <N4L:makesObservation rdfs:resource="{concat('http://doi.org/',../../@doi,generate-id(/interchange:observational-data/interchange:observation/@ontology-class))}"/>
       </rdfs:Resource>

        <rdfs:Resource>
            <xsl:attribute name="rdf:about"><xsl:value-of select="@method-class" /></xsl:attribute>
            <rdfs:subClassOf rdf:resource="http://doi.org/10.1601/Method" />
        </rdfs:Resource>
    </xsl:template> -->
    
</xsl:stylesheet>