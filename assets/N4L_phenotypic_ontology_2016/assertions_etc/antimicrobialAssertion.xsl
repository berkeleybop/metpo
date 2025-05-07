<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  xmlns:exsl="http://exslt.org/common" exclude-result-prefixes="exsl" version="1.0">
    
<xsl:output method="xml" standalone="no" encoding="UTF-8" omit-xml-declaration="no" indent="yes" />
    <xsl:template match="/">
        <xsl:for-each select="entities/entity">            
            <xsl:variable name="phenotype">
                <xsl:value-of select="assertion/@class"/>
            </xsl:variable>   
            <xsl:variable name="substance">
                <xsl:value-of select="assertion/observational-data/condition/text/named-content/@measurement-uri"/>
            </xsl:variable>
            <entity doi="{concat('http://doi.org/',@doi)}">
           <assertion>
               <phenotype class-uri="{$phenotype}" substance-uri="{$substance}"/>
           </assertion>
         </entity>
       </xsl:for-each>
</xsl:template>
</xsl:stylesheet>