<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:interchange="http://namesforlife.com/ns/interchange" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:exsl="http://exslt.org/common" xmlns:N4L="http://doi.org/10.1601/" xmlns:compound="http://rdf.ncbi.nlm.nih.gov/pubchem/compound/" xmlns:obo="http://purl.obolibrary.org/obo/" xmlns:media="http://doi.org/10.1601/media/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" exclude-result-prefixes="exsl" version="1.0">
    
<xsl:output method="xml" standalone="no" encoding="UTF-8" omit-xml-declaration="no" indent="yes" />
    
    <xsl:strip-space elements="*" />
    <xsl:output indent="yes" />    
    <xsl:template match="/interchange:entities">
        
    <rdf:RDF xmlns:N4L="http://doi.org/10.1601/" xmlns:obo="http://purl.obolibrary.org/obo/" xmlns:media="http://doi.org/10.1601/media/" xmlns:unit="http://doi.org/10.1601/unit/" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:xsd="http://www.w3.org/2001/XMLSchema#">

    <owl:Ontology rdf:about="http://doi.org/10.1601/">
    <owl:imports rdf:resource="http://doi.org/10.1601/"/>
    <owl:imports rdf:resource="http://purl.obolibrary.org/obo/"/>
    <owl:imports rdf:resource="http://doi.org/10.1601/media/"/>
    <owl:imports rdf:resource="http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"/>
    <owl:imports rdf:resource="http://doi.org/10.1601/unit/"/>
    </owl:Ontology>        
        <xsl:apply-templates select="interchange:entity"/>         
    </rdf:RDF>

    </xsl:template>
   
    <xsl:template match="interchange:entity">
        <xsl:apply-templates select="interchange:assertion"/>
    </xsl:template>
    
    <xsl:template match="interchange:assertion"> 
        <xsl:apply-templates select="interchange:observational-data"/>        
    </xsl:template>
    
    <xsl:template match="interchange:observational-data">
        <xsl:apply-templates select="interchange:observation"/>
        <xsl:apply-templates select="interchange:phenotype"/> 
        <xsl:apply-templates select="interchange:condition"/> 
        <xsl:apply-templates select="interchange:cellular-activity"/>
        <xsl:apply-templates select="interchange:inclusion-body"/>
    </xsl:template>
    
    <xsl:template match="interchange:inclusion-body">
        
        <rdfs:Resource rdf:about="{concat('http://doi.org/', ../../../@doi)}">
            <N4L:hasOrganismObservation rdf:resource = "{concat('http://doi.org/',../../../@doi,'_',../../@source,'_OrganismObservation')}"/>
        </rdfs:Resource>
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,'_',../../@source,'_OrganismObservation')}">
            <rdf:type rdf:resource="http://doi.org/10.1601/OrganismObservation"/>
            <N4L:hasInclusionBodyObservation rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(@class-uri),'_inclusionBodyObservation')}"/>
        </rdfs:Resource>
        
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(@class-uri),'_inclusionBodyObservation')}">
            <rdf:type rdf:resource="{@class-uri}"/>     
            <xsl:if test="../following-sibling::interchange:method/@class-uri">
                <!-- added: 2016-03-30 -->
                <N4L:hasMethod rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
            </xsl:if>
        </rdfs:Resource>
        
        <xsl:if test="../following-sibling::interchange:method/@class-uri">
            <!-- added: 2016-03-30 -->
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
            <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>            
        </rdfs:Resource>
        </xsl:if>
        
    </xsl:template>
    
    <xsl:template match="interchange:condition">
        
        <!--<xsl:apply-templates select="interchange:substance-class"/>-->
        
        <xsl:variable name="countCondition"><xsl:value-of select="count(../interchange:condition)"/></xsl:variable>
        
        <!--<xsl:variable name="substanceValue">
        <xsl:for-each select="./interchange:substance/@class-uri">
            <xsl:value-of select="concat(generate-id(./interchange:substance/@class-uri),_)"/>          
        </xsl:for-each>
        </xsl:variable>
        -->     
        
        <xsl:if test="$countCondition =1">
            
        <xsl:apply-templates select="interchange:substance"/>
        <xsl:apply-templates select="interchange:measurement"/>               
            
            <xsl:if test="@class-uri">
                <xsl:if test="../interchange:observation/@class-uri">
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_','GrowthObservation')}">
            <rdf:type rdf:resource="{../interchange:observation/@class-uri}"/>
                
                <xsl:if test="../following-sibling::interchange:method/@class-uri">
                    <!-- added: 2016-03-30 -->
                    <N4L:hasMethod rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
                </xsl:if>
                
            <!-- added: 2016-03-05 -->
            <N4L:hasCondition rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_',generate-id(@class-uri),'_','Condition')}"/>
            </rdfs:Resource>
            <!-- added: 2016-03-05 -->
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_',generate-id(@class-uri),'_','Condition')}">
            <rdf:type rdf:resource="{@class-uri}"/>
            </rdfs:Resource>
                    
                    <xsl:if test="../following-sibling::interchange:method/@class-uri">
                    
                        <!-- added: 2016-03-30 -->
                        
                        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
                            <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>            
                        </rdfs:Resource>
                    </xsl:if>
                    
                </xsl:if>
            </xsl:if>
            
        </xsl:if>

        <xsl:if test="$countCondition &gt;1">
            
            <xsl:if test="../interchange:observation/@class-uri">
        
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_','GrowthObservation')}">
                    <rdf:type rdf:resource="{../interchange:observation/@class-uri}"/>
                    <N4L:hasComponentCondition rdf:resource = "{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_','ComponentCondition')}"/>
                    <xsl:if test="../following-sibling::interchange:method/@class-uri">
                        <!-- added: 2016-03-30 -->
                        <N4L:hasMethod rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
                    </xsl:if>
                    
                </rdfs:Resource>
                
                <xsl:if test="../following-sibling::interchange:method/@class-uri">
                    
                    <!-- added: 2016-03-30 -->
                    
                    <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
                        <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>            
                    </rdfs:Resource>
                </xsl:if>
                
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_','ComponentCondition')}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/media/Component"/>
                    <rdf:type rdf:resource="{../../interchange:observational-data/@class-uri}"/>
                    <media:containsIngredient  rdf:resource = "{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_',generate-id(.//@class-uri),'_','Ingredient')}"/>
                </rdfs:Resource>
              
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_',generate-id(.//@class-uri),'_','Ingredient')}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/media/Ingredient"/>
                    
                    <media:hasSubstance rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_',generate-id(.//@class-uri),'_','Substance')}"/>
                    
                    <xsl:if test=".//interchange:unit/@class-uri">
                    <media:hasMeasure rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_',generate-id(.//interchange:unit/@class-uri),'_','Measure')}"/>
                    </xsl:if>
                    
                    <xsl:if test=".//interchange:value/text()">
                        <media:hasConcentration rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_',generate-id(.//@class-uri),'_','Concentration')}"/>
                    </xsl:if>
                
                </rdfs:Resource>
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_',generate-id(.//@class-uri),'_','Substance')}">
                    <rdf:type rdf:resource="{.//@class-uri}"/>                   
                </rdfs:Resource>
                
                <xsl:if test=".//interchange:unit/@class-uri">
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_',generate-id(.//interchange:unit/@class-uri),'_','Measure')}">
                    <rdf:type rdf:resource="{.//interchange:unit/@class-uri}"/>                   
                </rdfs:Resource>
                </xsl:if>
                
                <xsl:if test=".//interchange:value/text()">
                <xsl:variable name= "ingredientValueObservation">
                    <xsl:value-of select=".//interchange:value/text()"/>
                </xsl:variable>
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:observation/@class-uri),'_',generate-id(.//@class-uri),'_','Concentration')}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/media/Concentration"/>   
                    <media:hasIngredientConcentrationValue rdf:datatype="http://www.w3.org/2001/XMLSchema#double"><xsl:value-of select="$ingredientValueObservation"/></media:hasIngredientConcentrationValue>   
                </rdfs:Resource>
                </xsl:if>
            
            </xsl:if>
            
            <xsl:if test="../interchange:cellular-activity/@class-uri">

                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:cellular-activity/@class-uri),'_','CellularActivity')}">
                    
                    <N4L:hasCellularActivityOfComponent rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:cellular-activity/@class-uri),'_','CellularActivityOfComponent')}"/>
                    
                    <xsl:if test="../following-sibling::interchange:method/@class-uri">
                        <!-- added: 2016-03-30 -->
                        <N4L:hasMethod rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
                    </xsl:if>
                    
                </rdfs:Resource>
            
                <xsl:if test="../following-sibling::interchange:method/@class-uri">
                    
                    <!-- added: 2016-03-30 -->
                    
                    <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
                        <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>            
                    </rdfs:Resource>
                </xsl:if>
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:cellular-activity/@class-uri),'_','CellularActivityOfComponent')}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/media/Component"/>
                    <media:containsIngredient  rdf:resource = "{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:cellular-activity/@class-uri),'_',generate-id(.//@class-uri),'_','Ingredient')}"/>
                </rdfs:Resource>
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:cellular-activity/@class-uri),'_',generate-id(.//@class-uri),'_','Ingredient')}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/media/Ingredient"/>
                    
                    <media:hasSubstance rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:cellular-activity/@class-uri),'_',generate-id(.//@class-uri),'_','Substance')}"/>
                    
                    <xsl:if test=".//interchange:unit/@class-uri">
                    <media:hasMeasure rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:cellular-activity/@class-uri),'_',generate-id(.//interchange:unit/@class-uri),'_','Measure')}"/>
                    </xsl:if>
                    
                    <xsl:if test=".//interchange:value/text()">
                    <media:hasConcentration rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:cellular-activity/@class-uri),'_',generate-id(.//@class-uri),'_','Concentration')}"/>
                    </xsl:if>
                    
                </rdfs:Resource>
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:cellular-activity/@class-uri),'_',generate-id(.//@class-uri),'_','Substance')}">
                    <rdf:type rdf:resource="{.//@class-uri}"/>                   
                </rdfs:Resource>
                
                <xsl:if test=".//interchange:unit/@class-uri">
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:cellular-activity/@class-uri),'_',generate-id(.//interchange:unit/@class-uri),'_','Measure')}">
                    <rdf:type rdf:resource="{.//interchange:unit/@class-uri}"/>                   
                </rdfs:Resource>
                </xsl:if>
                
                <xsl:if test=".//interchange:value/text()">
                <xsl:variable name= "ingredientValueCellularActivity">
                    <xsl:value-of select=".//interchange:value/text()"/>
                </xsl:variable>
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:cellular-activity/@class-uri),'_',generate-id(.//@class-uri),'_','Concentration')}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/media/Concentration"/>   
                    <media:hasIngredientConcentrationValue rdf:datatype="http://www.w3.org/2001/XMLSchema#double"><xsl:value-of select="$ingredientValueCellularActivity"/></media:hasIngredientConcentrationValue>   
                </rdfs:Resource>
                </xsl:if>
                
            </xsl:if>
        
            <xsl:if test="../interchange:phenotype/@class-uri">
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:phenotype/@class-uri),'_','GrowthObservation')}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/GrowthObservation"/> 
                    <N4L:hasComponentCondition rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:phenotype/@class-uri),'_','ComponentCondition')}"/>
                    
                    <xsl:if test="../following-sibling::interchange:method/@class-uri">
                        <!-- added: 2016-03-30 -->
                        <N4L:hasMethod rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
                    </xsl:if>
                    
                </rdfs:Resource>
                
                <xsl:if test="../following-sibling::interchange:method/@class-uri">
                    
                    <!-- added: 2016-03-30 -->
                    
                    <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
                        <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>            
                    </rdfs:Resource>
                </xsl:if>
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:phenotype/@class-uri),'_','ComponentCondition')}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/media/Component"/>
                    <rdf:type rdf:resource="{../../interchange:observational-data/@class-uri}"/>
                    <media:containsIngredient  rdf:resource = "{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:phenotype/@class-uri),'_',generate-id(.//@class-uri),'_','Ingredient')}"/>
                </rdfs:Resource>
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:phenotype/@class-uri),'_',generate-id(.//@class-uri),'_','Ingredient')}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/media/Ingredient"/>
                    <media:hasSubstance rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:phenotype/@class-uri),'_',generate-id(.//@class-uri),'_','Substance')}"/>
                    
                    <xsl:if test=".//interchange:unit/@class-uri">
                    <media:hasMeasure rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:phenotype/@class-uri),'_',generate-id(.//interchange:unit/@class-uri),'_','Measure')}"/>                    
                    </xsl:if>
                    
                    <xsl:if test=".//interchange:value/text()">
                        <media:hasConcentration rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:phenotype/@class-uri),'_',generate-id(.//@class-uri),'_','Concentration')}"/>
                    </xsl:if>
                    
                </rdfs:Resource>
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:phenotype/@class-uri),'_',generate-id(.//@class-uri),'_','Substance')}">
                    <rdf:type rdf:resource="{.//@class-uri}"/>                   
                </rdfs:Resource>
                
                <xsl:if test=".//interchange:unit/@class-uri">
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:phenotype/@class-uri),'_',generate-id(.//interchange:unit/@class-uri),'_','Measure')}">
                    <rdf:type rdf:resource="{.//interchange:unit/@class-uri}"/>                   
                </rdfs:Resource>
                </xsl:if>
                
                <xsl:if test=".//interchange:value/text()">
                <xsl:variable name= "ingredientValueObservation">
                    <xsl:value-of select=".//interchange:value/text()"/>
                </xsl:variable>
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../interchange:phenotype/@class-uri),'_',generate-id(.//@class-uri),'_','Concentration')}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/media/Concentration"/>   
                    <media:hasIngredientConcentrationValue rdf:datatype="http://www.w3.org/2001/XMLSchema#double"><xsl:value-of select="$ingredientValueObservation"/></media:hasIngredientConcentrationValue>   
                </rdfs:Resource>
                </xsl:if>
                
            </xsl:if>
            
        </xsl:if>
        
    </xsl:template>
    
    <xsl:template match="interchange:measurement">
        <xsl:apply-templates select="interchange:unit"/>
        <xsl:apply-templates select="interchange:value"/>
    </xsl:template>
    
    <xsl:template match="interchange:cellular-activity">
        
        <rdfs:Resource rdf:about="{concat('http://doi.org/', ../../../@doi)}">
            <rdf:type rdf:resource="http://doi.org/10.1601/Strain"/>
            <N4L:hasOrganismObservation rdf:resource = "{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(@class-uri),'_','Observation')}"/>            
        </rdfs:Resource>
        
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(@class-uri),'_','Observation')}">
            <rdf:type rdf:resource="http://doi.org/10.1601/OrganismObservation"/> 
            <N4L:hasCellularActivity rdf:resource = "{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(@class-uri),'_','CellularActivity')}"/>
            <N4L:hasDocumentResource rdf:resource="{concat('http://doi.org/10.1601/',../../@source)}"/>
        </rdfs:Resource>
        
        <xsl:if test="../following-sibling::interchange:method/@class-uri">
            <!-- added : 2016-03-30. -->
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
            <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>
        </rdfs:Resource>
        </xsl:if>
        
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(@class-uri),'_','CellularActivity')}">
            <rdf:type rdf:resource="{@class-uri}"/>
            
            <xsl:if test="../following-sibling::interchange:method/@class-uri">
                <!-- added : 2016-03-30. -->
                <N4L:hasMethod  rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
            </xsl:if> 
            
        </rdfs:Resource>
        
        <rdfs:Resource rdf:about="{concat('http://doi.org/10.1601/',../../@source)}">
            <rdf:type rdf:resource="http://doi.org/10.1601/DocumentResource"/>
        </rdfs:Resource>
    
        <!--  <xsl:if test="@class-uri='http://doi.org/10.1601/Respiration'">-->
           
            <!-- added: 2016-03-24 -->
            <xsl:if test="following-sibling::interchange:condition/@class-uri='http://doi.org/10.1601/Anoxic'">
              
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(@class-uri),'_','Observation')}">
                    <N4L:composedOf rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(following-sibling::interchange:condition/@class-uri),'_','GrowthObservation')}"/>
                </rdfs:Resource>
                
                <xsl:if test="../following-sibling::interchange:method/@class-uri">
                    <!-- added : 2016-03-30. -->
                    <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
                        <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>
                    </rdfs:Resource>
                </xsl:if>
                
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(following-sibling::interchange:condition/@class-uri),'_','GrowthObservation')}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/Growth"/>
                    <N4L:hasCondition rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(following-sibling::interchange:condition/@class-uri),'_',generate-id(@class-uri),'_','AnoxicCondition')}"/>
                    
                    <xsl:if test="../following-sibling::interchange:method/@class-uri">
                        <!-- added : 2016-03-30. -->
                        <N4L:hasMethod  rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
                    </xsl:if>
                    
                </rdfs:Resource>
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(following-sibling::interchange:condition/@class-uri),'_',generate-id(@class-uri),'_','AnoxicCondition')}">
                    <rdf:type rdf:resource="{following-sibling::interchange:condition/@class-uri}"/>
                </rdfs:Resource>
       <!--     </xsl:if>    -->        
        </xsl:if>
        
    </xsl:template>
    
    <xsl:template match="interchange:observation">
        <xsl:choose>
        <xsl:when test="//interchange:condition/@class-uri">
        
            <rdfs:Resource rdf:about="{concat('http://doi.org/', ../../../@doi)}">
        
            <rdf:type rdf:resource="http://doi.org/10.1601/Strain"/>
            <!--<N4L:hasOrganismObservation rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source ,'_',generate-id(@class-uri),'_','Observation')}"/>-->
            <N4L:hasOrganismObservation rdf:resource="{concat('http://doi.org/',../../../@doi,'_','OrganismObservation')}"/>                          
            </rdfs:Resource>
        
            <!--<rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi, ../../@source ,'_',generate-id(@class-uri),'_','Observation')}">-->

            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,'_','OrganismObservation')}">
            <rdf:type rdf:resource="http://doi.org/10.1601/OrganismObservation"/>
            <N4L:composedOf rdf:resource ="{concat('http://doi.org/',../../../@doi,../../@source, '_',generate-id(@class-uri),'_','GrowthObservation')}"/>
            <N4L:hasDocumentResource rdf:resource="{concat('http://doi.org/10.1601/',../../@source)}"/>
        </rdfs:Resource>
        
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source, '_',generate-id(@class-uri),'_','GrowthObservation')}">
                
                <xsl:if test="../following-sibling::interchange:method/@class-uri">
                    <!-- added : 2016-03-30. -->
                    <N4L:hasMethod  rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
                </xsl:if>
                
            </rdfs:Resource>
       
            
            <xsl:if test="../following-sibling::interchange:method/@class-uri">
       
                <!-- added : 2016-03-30. -->
           
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
       
               <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>
       
           
                </rdfs:Resource>
       
       </xsl:if>
            
        <rdfs:Resource rdf:about="{concat('http://doi.org/10.1601/',../../@source)}">
            <rdf:type rdf:resource="http://doi.org/10.1601/DocumentResource"/>    
        </rdfs:Resource>
            
        </xsl:when>
            <xsl:otherwise>
                <rdfs:Resource rdf:about="{concat('http://doi.org/', ../../../@doi)}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/Strain"/>
                    <N4L:hasOrganismObservation rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source ,'_',generate-id(@class-uri),'_','OrganismObservation')}"/>
                    <!--<N4L:hasOrganismObservation rdf:resource="{concat('http://doi.org/',../../../@doi,'_','OrganismObservation')}"/>     -->     
                </rdfs:Resource>
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi, ../../@source ,'_',generate-id(@class-uri),'_','OrganismObservation')}">
                <!--<rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,'_','OrganismObservation')}">-->
                    <rdf:type rdf:resource="http://doi.org/10.1601/OrganismObservation"/>
                    <N4L:composedOf rdf:resource ="{concat('http://doi.org/',../../../@doi,../../@source, '_',generate-id(@class-uri),'_','GrowthObservation')}"/>
                    <N4L:hasDocumentResource rdf:resource="{concat('http://doi.org/10.1601/',../../@source)}"/>
                    
                </rdfs:Resource>
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source, '_',generate-id(@class-uri),'_','GrowthObservation')}">

                    <xsl:if test="../following-sibling::interchange:method/@class-uri">
                        <!-- added : 2016-03-30. -->
                        <N4L:hasMethod  rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
                    </xsl:if> 
                    
                </rdfs:Resource>
                
                <xsl:if test="../following-sibling::interchange:method/@class-uri">
                    <!-- added : 2016-03-30. -->                    
                    <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
                        <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>
                    </rdfs:Resource>
                    
                </xsl:if>
                
                <rdfs:Resource rdf:about="{concat('http://doi.org/10.1601/',../../@source)}">
                    <rdf:type rdf:resource="http://doi.org/10.1601/DocumentResource"/>    
                </rdfs:Resource>
            </xsl:otherwise>
            </xsl:choose>
        
   </xsl:template>
    
   <xsl:template match="interchange:phenotype">
       <xsl:choose>
           <xsl:when test=".././/interchange:substance/@class-uri">
        <rdfs:Resource rdf:about="{concat('http://doi.org/', ../../../@doi)}">
            <rdf:type rdf:resource="http://doi.org/10.1601/Strain"/>
            <N4L:hasOrganismObservation rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source ,'_',generate-id(@class-uri),'_','Observation')}"/>
        </rdfs:Resource>
       <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source ,'_',generate-id(@class-uri),'_','Observation')}">
            <rdf:type rdf:resource="http://doi.org/10.1601/OrganismObservation"/>
           <N4L:hasAtomicObservationPhenotype rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source ,'_',generate-id(@class-uri),'_','Phenotype')}"/>
           <N4L:composedOf rdf:resource ="{concat('http://doi.org/',../../../@doi,../../@source ,'_',generate-id(@class-uri),'_','GrowthObservation')}"/>
           <N4L:hasDocumentResource rdf:resource="{concat('http://doi.org/10.1601/',../../@source)}"/>
           
           
           
        </rdfs:Resource>
               
               <xsl:if test="../following-sibling::interchange:method/@class-uri">
                   <!-- added : 2016-03-30. -->                    
                   <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
                       <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>
                   </rdfs:Resource>
                   
               </xsl:if>
               
       <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source ,'_',generate-id(@class-uri),'_','Phenotype')}">
            <rdf:type rdf:resource="{@class-uri}"/>    
        </rdfs:Resource>  
       <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source ,'_',generate-id(@class-uri),'_','GrowthObservation')}">
            <rdf:type rdf:resource="http://doi.org/10.1601/GrowthObservation"/>    
           <xsl:if test="../following-sibling::interchange:method/@class-uri">
               <!-- added : 2016-03-30. -->
               <N4L:hasMethod  rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
           </xsl:if> 
        </rdfs:Resource>
       <rdfs:Resource rdf:about="{concat('http://doi.org/10.1601/',../../@source)}">
           <rdf:type rdf:resource="http://doi.org/10.1601/DocumentResource"/>    
       </rdfs:Resource>
           </xsl:when>
           <xsl:otherwise>
               <rdfs:Resource rdf:about="{concat('http://doi.org/', ../../../@doi)}">
                   
                   <rdf:type rdf:resource="http://doi.org/10.1601/Strain" />
                   
                   <N4L:hasPhenotype rdf:resource="{concat('http://doi.org/',../../../@doi,'_Phenotype')}"/> 
                   <!-- added 2016-03-11 -->
                   <N4L:hasOrganismObservation rdf:resource="{concat('http://doi.org/',../../../@doi,'_','OrganismObservation')}"/>
               </rdfs:Resource>
               <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,'_Phenotype')}">
                   <rdf:type rdf:resource="{@class-uri}"/>    
                   <xsl:if test="../following-sibling::interchange:method/@class-uri">
                       <!-- added : 2016-03-30. -->
                       <N4L:hasMethod  rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
                   </xsl:if>
               </rdfs:Resource>
               <!-- added 2016-03-11 -->
               <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,'_','OrganismObservation')}">
                   <N4L:hasDocumentResource rdf:resource="{concat('http://doi.org/10.1601/',../../@source)}"/>
                   <rdf:type rdf:resource="http://doi.org/10.1601/OrganismObservation"/>
                   <!--<N4L:hasGrowthObservation rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source ,'_',generate-id(@class-uri),'_','GrowthObservation')}"/>-->                  
                   
               </rdfs:Resource>
               
               <xsl:if test="../following-sibling::interchange:method/@class-uri">
                   <!-- added : 2016-03-30. -->                    
                   <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
                       <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>
                   </rdfs:Resource>
                   
               </xsl:if>
               
               <rdfs:Resource rdf:about="{concat('http://doi.org/10.1601/',../../@source)}">
                   <rdf:type rdf:resource="http://doi.org/10.1601/DocumentResource"/>
               </rdfs:Resource>
               
           </xsl:otherwise>
       </xsl:choose>    
    </xsl:template>    
    
<!--<xsl:template match="interchange:substance-class">   
        <xsl:variable name="substanceClass"><xsl:value-of select="generate-id()"/></xsl:variable>
        
        <xsl:if test="../../interchange:observation/@class-uri">
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source,'_',generate-id(../../interchange:observation/@class-uri),'_','GrowthObservation')}">
            <rdf:type rdf:resource="http://doi.org/10.1601/GrowthObservation"/> 
                <N4L:hasSubstanceGroupCondition rdf:resource = "{concat('http://doi.org/',../../../@doi,../../../../@source,'_',$substanceClass,'_','SubstanceClassCondition')}" />
        </rdfs:Resource>
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source,'_',$substanceClass,'_','SubstanceClassCondition')}">
            <rdf:type><xsl:attribute name="rdf:resource"><xsl:value-of select="."/></xsl:attribute></rdf:type>
        </rdfs:Resource>
        </xsl:if>
        
        <xsl:if test="../../interchange:phenotype/@class-uri">
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source,'_',generate-id(../../interchange:phenotype/@class-uri),'_','GrowthObservation')}">
                <rdf:type rdf:resource="http://doi.org/10.1601/GrowthObservation"/> 
                <N4L:hasSubstanceGroupCondition rdf:resource = "{concat('http://doi.org/',../../../../@doi,../../../@source,'_',$substanceClass,'_','SubstanceClassCondition')}" />
            </rdfs:Resource>
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source,'_',$substanceClass,'_','SubstanceClassCondition')}">
                <rdf:type><xsl:attribute name="rdf:resource"><xsl:value-of select="."/></xsl:attribute></rdf:type>
            </rdfs:Resource>
        </xsl:if>
    </xsl:template>-->
    
    <xsl:template match="interchange:substance">
    
    <!-- <xsl:variable name= "substance">
         <xsl:value-of select="generate-id(self::node())"/>
         </xsl:variable> 
    -->
        
        <xsl:if test="../../interchange:observation/@class-uri">
        
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source,'_',generate-id(../../interchange:observation/@class-uri),'_','GrowthObservation')}">
            <rdf:type rdf:resource="http://doi.org/10.1601/GrowthObservation"/> 
            <!-- added: 2016-03-15. -->
            <rdf:type rdf:resource="{../../interchange:observation/@class-uri}"/>
            <N4L:hasSubstanceCondition rdf:resource="{concat('http://doi.org/',../../../../@doi,../../../@source ,'_',generate-id(@class-uri),'_','SubstanceCondition')}"/>                
        </rdfs:Resource>
        
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source,'_',generate-id(../../interchange:observation/@class-uri),'_','GrowthObservation')}">
                <xsl:if test="../following-sibling::interchange:method/@class-uri">
                    <!-- added : 2016-03-30. -->
                    <N4L:hasMethod  rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
                </xsl:if> 
            </rdfs:Resource>
            
            <xsl:if test="../following-sibling::interchange:method/@class-uri">
                <!-- added : 2016-03-30. -->                    
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
                    <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>
                </rdfs:Resource>
                
            </xsl:if>
            
            
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source ,'_',generate-id(@class-uri),'_','SubstanceCondition')}">
            <rdf:type rdf:resource="{@class-uri}"/>
            
            <xsl:if test="@biological-role">
                <!-- biological role can be asserted with observation (growth/no growth). added: 20151207-->
            <media:hasBiologicalRole rdf:resource="{concat('http://doi.org/',../../../../@doi,../../../@source ,'_',generate-id(@biological-role),'_','BiologicalRole')}"/>
            </xsl:if>
        
        </rdfs:Resource>
         
            <xsl:if test="@biological-role">
                <!-- biological role can be asserted with observation (growth/no growth). added: 20151207 -->
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source ,'_',generate-id(@biological-role),'_','BiologicalRole')}">
                    <rdf:type rdf:resource ="{@biological-role}"/>
                </rdfs:Resource>
            </xsl:if> 
            
        </xsl:if>
        
        <xsl:if test="../../interchange:phenotype/@class-uri">
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source,'_',generate-id(../../interchange:phenotype/@class-uri),'_','GrowthObservation')}">
                <rdf:type rdf:resource="http://doi.org/10.1601/GrowthObservation"/> 
                
                <xsl:if test="../following-sibling::interchange:method/@class-uri">
                    <!-- added : 2016-03-30. -->
                    <N4L:hasMethod  rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
                </xsl:if> 
                
                <N4L:hasSubstanceCondition rdf:resource="{concat('http://doi.org/',../../../../@doi,../../../@source ,'_',generate-id(@class-uri),'_','SubstanceCondition')}"/>
            </rdfs:Resource>
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source ,'_',generate-id(@class-uri),'_','SubstanceCondition')}">            
                <rdf:type rdf:resource="{@class-uri}"/>
            </rdfs:Resource>
            
            <xsl:if test="../following-sibling::interchange:method/@class-uri">
                <!-- added : 2016-03-30. -->                    
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
                    <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>
                </rdfs:Resource>
                
            </xsl:if>
            
        </xsl:if>
        
        <xsl:if test="../../interchange:condition/@MIC='true'">
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi)}">
                <N4L:hasMinimumInhibitoryConcentration rdf:resource="{concat('http://doi.org/',../../../../@doi,../../../@source ,'_',generate-id(@class-uri),'_','SubstanceCondition')}"/>
            </rdfs:Resource>
        </xsl:if>
        
        <xsl:if test="../../interchange:cellular-activity/@class-uri">
            <!-- Cellular activity of an asserted substance. added: 20151207-->
            
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source,'_',generate-id(../../interchange:cellular-activity/@class-uri),'_','CellularActivity')}">
                <N4L:hasCellularActivityOfSubstance rdf:resource="{concat('http://doi.org/',../../../../@doi,../../../@source ,'_',generate-id(@class-uri),'_','CelullarActivityOfSubstance')}"/>
                <xsl:if test="../following-sibling::interchange:method/@class-uri">
                    <!-- added : 2016-03-30. -->
                    <N4L:hasMethod  rdf:resource="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}"/>
                </xsl:if>
            
            </rdfs:Resource>
            
            <xsl:if test="../following-sibling::interchange:method/@class-uri">
                <!-- added : 2016-03-30. -->                    
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../@doi,../../@source,'_',generate-id(../following-sibling::interchange:method/@class-uri),'_methodObservation')}">
                    <rdf:type rdf:resource="{../following-sibling::interchange:method/@class-uri}"/>
                </rdfs:Resource>
                
            </xsl:if>
            
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source ,'_',generate-id(@class-uri),'_','CelullarActivityOfSubstance')}">
              <rdf:type rdf:resource ="{@class-uri}"/>
                <xsl:if test="@biological-role">
                <media:hasBiologicalRole rdf:resource="{concat('http://doi.org/',../../../../@doi,../../../@source ,'_',generate-id(@biological-role),'_','BiologicalRole')}"/>
                </xsl:if>
            </rdfs:Resource>
            
            <xsl:if test="@biological-role">
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../@doi,../../../@source ,'_',generate-id(@biological-role),'_','BiologicalRole')}">
                    <rdf:type rdf:resource ="{@biological-role}"/>
                </rdfs:Resource>
            </xsl:if>
            
        </xsl:if>
        
        
    </xsl:template>  
    
    <xsl:template match="interchange:unit">
        <xsl:variable name= "unit">
            <xsl:value-of select="generate-id(self::node())"/>
        </xsl:variable>
        <xsl:variable name= "substance">
            <xsl:value-of select="generate-id(../../interchange:substance/@class-uri)"/>
        </xsl:variable>
        
        <xsl:variable name= "condition">
            <!-- addded: 2016-03-04 -->
            <xsl:value-of select="generate-id(../../interchange:condition/@class-uri)"/>
        </xsl:variable>
        
        <xsl:if test="../../../interchange:phenotype/@class-uri">
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$substance,'_','SubstanceCondition')}">
            <rdf:type><xsl:attribute name="rdf:resource"><xsl:value-of select="../../interchange:substance/@class-uri"/></xsl:attribute></rdf:type>
            <N4L:hasUnit rdf:resource ="{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$substance,'_',$unit,'_','Unit')}"/>
        </rdfs:Resource> 
        <rdfs:Resource rdf:about = "{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$substance,'_',$unit,'_','Unit')}">
            <rdf:type rdf:resource ="{@class-uri}"/>
        </rdfs:Resource>
        </xsl:if>
        
        <xsl:if test="../../../interchange:observation/@class-uri">
            
            <xsl:if test="../../interchange:substance/@class-uri">
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$substance,'_','SubstanceCondition')}">
                <rdf:type><xsl:attribute name="rdf:resource"><xsl:value-of select="../../interchange:substance/@class-uri"/></xsl:attribute></rdf:type>
                <N4L:hasUnit rdf:resource ="{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$substance,'_',$unit,'_','Unit')}"/>
            </rdfs:Resource> 
            <rdfs:Resource rdf:about = "{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$substance,'_',$unit,'_','Unit')}">
                <rdf:type rdf:resource ="{@class-uri}"/>
            </rdfs:Resource>
            </xsl:if>
            
            <xsl:if test="../../../interchange:condition/@class-uri">
                <!-- addded: 2016-03-04 -->
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',generate-id(../../../interchange:observation/@class-uri),'_',generate-id(../../../interchange:condition/@class-uri),'_','Condition')}">
                    <N4L:hasUnit rdf:resource ="{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$condition,'_',$unit,'_','Unit')}"/>
                </rdfs:Resource>
                <rdfs:Resource rdf:about = "{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$condition,'_',$unit,'_','Unit')}">
                    <rdf:type rdf:resource ="{@class-uri}"/>
                </rdfs:Resource>
            </xsl:if>
        </xsl:if>
        
        <xsl:if test="../../../interchange:cellular-activity/@class-uri">
            
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$substance,'_','CelullarActivityOfSubstance')}">
                <rdf:type><xsl:attribute name="rdf:resource"><xsl:value-of select="../../interchange:substance/@class-uri"/></xsl:attribute></rdf:type>
                <N4L:hasUnit rdf:resource ="{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$substance,'_',$unit,'_','Unit')}"/>
            </rdfs:Resource> 
            <rdfs:Resource rdf:about = "{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$substance,'_',$unit,'_','Unit')}">
                <rdf:type rdf:resource ="{@class-uri}"/>
            </rdfs:Resource>
        </xsl:if>
        
        
    </xsl:template>
    
    <xsl:template match="interchange:value">
        <xsl:variable name= "value">
            <xsl:value-of select="."/>
        </xsl:variable>
        <xsl:variable name= "substance">
            <xsl:value-of select="generate-id(../../interchange:substance/@class-uri)"/>
        </xsl:variable>
        
        
        <xsl:if test="../../../interchange:phenotype/@class-uri">
        <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$substance,'_','SubstanceCondition')}">
            <rdf:type><xsl:attribute name="rdf:resource"><xsl:value-of select="../../interchange:substance/@class-uri"/></xsl:attribute></rdf:type>       
            <N4L:hasEnvironmentalConditionValue rdf:datatype="http://www.w3.org/2001/XMLSchema#double"><xsl:value-of select="$value"/></N4L:hasEnvironmentalConditionValue>
        </rdfs:Resource> 
        </xsl:if>
    
        <xsl:if test="../../../interchange:observation/@class-uri">
            <xsl:if test="../../interchange:substance/@class-uri">
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$substance,'_','SubstanceCondition')}">
                <rdf:type><xsl:attribute name="rdf:resource"><xsl:value-of select="../../interchange:substance/@class-uri"/></xsl:attribute></rdf:type>       
                <N4L:hasEnvironmentalConditionValue rdf:datatype="http://www.w3.org/2001/XMLSchema#double"><xsl:value-of select="$value"/></N4L:hasEnvironmentalConditionValue>
            </rdfs:Resource> 
            </xsl:if>
            <xsl:if test="../../../interchange:condition/@class-uri">
                <!-- addded: 2016-03-04 -->
                <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',generate-id(../../../interchange:observation/@class-uri),'_',generate-id(../../../interchange:condition/@class-uri),'_','Condition')}">
                    <!--<rdf:type><xsl:attribute name="rdf:resource"><xsl:value-of select="../../interchange:substance/@class-uri"/></xsl:attribute></rdf:type>  -->     
                    <N4L:hasEnvironmentalConditionValue rdf:datatype="http://www.w3.org/2001/XMLSchema#double"><xsl:value-of select="$value"/></N4L:hasEnvironmentalConditionValue>                   
                </rdfs:Resource>
                
            </xsl:if>
            
        </xsl:if>
        
        <xsl:if test="../../../interchange:cellular-activity/@class-uri">
            <rdfs:Resource rdf:about="{concat('http://doi.org/',../../../../../@doi,../../../../@source,'_',$substance,'_','CelullarActivityOfSubstance')}">
                <rdf:type><xsl:attribute name="rdf:resource"><xsl:value-of select="../../interchange:substance/@class-uri"/></xsl:attribute></rdf:type>       
                <N4L:hasEnvironmentalConditionValue rdf:datatype="http://www.w3.org/2001/XMLSchema#double"><xsl:value-of select="$value"/></N4L:hasEnvironmentalConditionValue>
            </rdfs:Resource> 
        </xsl:if>
        
    </xsl:template>

</xsl:stylesheet>