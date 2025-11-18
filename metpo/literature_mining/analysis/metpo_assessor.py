"""
METPO Literature Mining Assessor

Two-phase assessment tool with clear CLI entrypoints:
1. Template analysis (design quality in isolation)
2. Extraction analysis (real-world performance)

Integrates with:
- semsql ontology registry for annotator validation
- OntoGPT extraction data model understanding
- Template pattern detection and cross-template optimization
"""

import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import click
import requests
import yaml


class MetpoAssessor:
    def __init__(self):
        self.semsql_registry = self._load_semsql_registry()
        self.universal_entities = {"pmid", "source_text"}

    def _load_semsql_registry(self) -> dict[str, Any]:
        """Load semsql ontology registry for annotator validation."""
        url = "https://raw.githubusercontent.com/INCATools/semantic-sql/refs/heads/main/src/semsql/builder/registry/ontologies.yaml"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return yaml.safe_load(response.text)
        except Exception as e:
            click.echo(f"Warning: Could not load semsql registry: {e}", err=True)
            return {}

    def _get_available_annotators(self) -> set[str]:
        """Extract available annotator prefixes from semsql registry."""
        annotators = set()
        if "ontologies" in self.semsql_registry:
            for ont_info in self.semsql_registry["ontologies"]:
                if isinstance(ont_info, dict) and "id" in ont_info:
                    annotators.add(f"sqlite:obo:{ont_info['id']}")
        return annotators

    # ===== PHASE 1: TEMPLATE ANALYSIS =====

    def analyze_template(self, template_path: Path) -> dict[str, Any]:
        """Analyze template design quality in isolation."""
        with Path(template_path).open() as f:
            template = yaml.safe_load(f)

        result = {
            "template_path": str(template_path),
            "template_name": template_path.stem,
            "analysis_timestamp": datetime.now(UTC).isoformat(),
            "compliance": {},
            "quality_metrics": {},
            "issues": [],
            "recommendations": [],
            "patterns": {},
        }

        classes = template.get("classes", {})

        # Core compliance checks
        result["compliance"] = {
            "tree_root_found": self._check_tree_root(classes),
            "compound_expressions": self._analyze_compound_expressions(classes),
            "semicolon_requests": self._check_semicolon_requests(classes),
            "multivalued_fields": self._check_multivalued_fields(classes),
            "annotator_quality": self._check_annotators(classes),
        }

        # Quality pattern detection
        result["patterns"] = self._detect_template_patterns(classes)

        # Generate issues and recommendations
        self._generate_template_recommendations(result)

        return result

    def _check_tree_root(self, classes: dict) -> dict[str, Any]:
        """Check tree root class structure."""
        tree_root = None
        for _class_name, class_def in classes.items():
            if class_def.get("tree_root"):
                tree_root = class_def
                break

        if not tree_root:
            return {"found": False}

        attributes = tree_root.get("attributes", {})
        return {
            "found": True,
            "attribute_count": len(attributes),
            "attributes": list(attributes.keys()),
        }

    def _analyze_compound_expressions(self, classes: dict) -> dict[str, Any]:
        """Analyze CompoundExpression classes for compliance."""
        compound_expressions = {}
        for class_name, class_def in classes.items():
            if class_def.get("is_a") == "CompoundExpression":
                compound_expressions[class_name] = class_def

        compliant_count = 0
        issues = []

        for ce_name, ce_def in compound_expressions.items():
            attrs = set(ce_def.get("attributes", {}).keys())
            expected = {"subject", "predicate", "object"}

            if attrs == expected:
                compliant_count += 1
            else:
                issues.append(f"{ce_name}: {attrs} != {expected}")

        return {
            "total_count": len(compound_expressions),
            "compliant_count": compliant_count,
            "compliance_rate": (compliant_count / max(len(compound_expressions), 1)) * 100,
            "issues": issues[:3],  # Limit output
        }

    def _check_semicolon_requests(self, classes: dict) -> dict[str, Any]:
        """Check if fields properly request semicolon-separated lists."""
        tree_root = self._find_tree_root(classes)
        if not tree_root:
            return {"total_fields": 0, "semicolon_fields": 0, "rate": 0}

        total_fields = 0
        semicolon_fields = 0

        for attr_name, attr_def in tree_root.get("attributes", {}).items():
            if attr_name in self.universal_entities:
                continue

            total_fields += 1
            description = attr_def.get("description", "").lower()

            if "semicolon" in description:
                semicolon_fields += 1

        return {
            "total_fields": total_fields,
            "semicolon_fields": semicolon_fields,
            "rate": (semicolon_fields / max(total_fields, 1)) * 100,
        }

    def _check_multivalued_fields(self, classes: dict) -> dict[str, Any]:
        """Check multivalued field usage."""
        tree_root = self._find_tree_root(classes)
        if not tree_root:
            return {"total_fields": 0, "multivalued_fields": 0, "rate": 0}

        total_fields = 0
        multivalued_fields = 0

        for attr_name, attr_def in tree_root.get("attributes", {}).items():
            if attr_name in self.universal_entities:
                continue

            total_fields += 1
            if attr_def.get("multivalued"):
                multivalued_fields += 1

        return {
            "total_fields": total_fields,
            "multivalued_fields": multivalued_fields,
            "rate": (multivalued_fields / max(total_fields, 1)) * 100,
        }

    def _check_annotators(self, classes: dict) -> dict[str, Any]:
        """Check NamedEntity annotator specifications."""
        available_annotators = self._get_available_annotators()

        named_entities = {}
        for class_name, class_def in classes.items():
            if class_def.get("is_a") == "NamedEntity":
                named_entities[class_name] = class_def

        total_entities = len(named_entities)
        well_annotated = 0
        annotator_issues = []

        for entity_name, entity_def in named_entities.items():
            annotators_str = entity_def.get("annotations", {}).get("annotators", "")

            if not annotators_str:
                annotator_issues.append(f"{entity_name}: No annotators")
                continue

            annotators = [a.strip() for a in annotators_str.split(",")]
            valid_annotators = []

            for annotator in annotators:
                if annotator.startswith("sqlite:obo:"):
                    if annotator in available_annotators:
                        valid_annotators.append(annotator)
                elif annotator in ["metpo.db"]:  # Special cases
                    valid_annotators.append(annotator)

            if len(valid_annotators) >= 2:
                well_annotated += 1
            elif len(valid_annotators) == 1:
                annotator_issues.append(f"{entity_name}: Only 1 annotator")
            else:
                annotator_issues.append(f"{entity_name}: No valid annotators")

        return {
            "total_entities": total_entities,
            "well_annotated": well_annotated,
            "rate": (well_annotated / max(total_entities, 1)) * 100,
            "issues": annotator_issues[:3],
        }

    def _detect_template_patterns(self, classes: dict) -> dict[str, Any]:
        """Detect good/bad patterns in template design."""
        patterns = {
            "good_practices": [],
            "anti_patterns": [],
            "entity_types": [],
            "predicate_types": [],
        }

        # Detect entity types and annotation patterns
        for class_name, class_def in classes.items():
            if class_def.get("is_a") == "NamedEntity":
                annotators = class_def.get("annotations", {}).get("annotators", "")
                patterns["entity_types"].append(
                    {
                        "name": class_name,
                        "annotators": annotators,
                        "description": class_def.get("description", "")[:100],
                    }
                )

        # Detect predicate enumeration patterns
        enums = classes.get("enums", {})
        for enum_name, enum_def in enums.items():
            if "Type" in enum_name or "Enum" in enum_name:
                values = enum_def.get("permissible_values", {})
                patterns["predicate_types"].append(
                    {
                        "name": enum_name,
                        "value_count": len(values),
                        "sample_values": list(values.keys())[:5],
                    }
                )

        return patterns

    def _generate_template_recommendations(self, result: dict):
        """Generate actionable recommendations for template improvement."""
        compliance = result["compliance"]

        # CompoundExpression compliance
        ce_rate = compliance["compound_expressions"]["compliance_rate"]
        if ce_rate < 100:
            result["issues"].append(f"CompoundExpression compliance: {ce_rate:.1f}%")
            result["recommendations"].append(
                "Fix CompoundExpression structure to use exactly subject/predicate/object"
            )

        # Semicolon request compliance
        semi_rate = compliance["semicolon_requests"]["rate"]
        if semi_rate < 80:
            result["issues"].append(f"Semicolon requests: {semi_rate:.1f}%")
            result["recommendations"].append("Add 'semicolon-separated list' to field descriptions")

        # Multivalued field compliance
        mv_rate = compliance["multivalued_fields"]["rate"]
        if mv_rate < 70:
            result["issues"].append(f"Multivalued fields: {mv_rate:.1f}%")
            result["recommendations"].append("Mark most fields as multivalued: true")

        # Annotator compliance
        ann_rate = compliance["annotator_quality"]["rate"]
        if ann_rate < 80:
            result["issues"].append(f"Well-annotated entities: {ann_rate:.1f}%")
            result["recommendations"].append(
                "Add multiple comma-separated annotators to NamedEntity classes"
            )

    # ===== PHASE 2: EXTRACTION ANALYSIS =====

    def analyze_extraction(self, extraction_path: Path) -> dict[str, Any]:
        """Analyze extraction output performance."""
        with Path(extraction_path).open() as f:
            docs = list(yaml.safe_load_all(f))

            if not docs:
                return self._empty_extraction_result(extraction_path)

            # Find ALL documents with extracted_object
            extractions = []
            for doc in docs:
                if isinstance(doc, dict) and "extracted_object" in doc:
                    extractions.append(doc)

            if not extractions:
                return self._empty_extraction_result(extraction_path)

        result = {
            "extraction_path": str(extraction_path),
            "template_name": self._extract_template_name(extraction_path),
            "analysis_timestamp": datetime.now(UTC).isoformat(),
            "abstracts_processed": len(extractions),
            "success_metrics": {},
            "performance": {},
            "issues": [],
            "strengths": [],
        }

        # Aggregate metrics across all extractions
        total_ce_count = 0
        successful_extractions = 0
        all_entities = []
        all_extracted_objects = []

        for extraction in extractions:
            extracted_obj = extraction.get("extracted_object", {})
            ce_count = self._count_compound_expressions(extracted_obj)
            total_ce_count += ce_count
            if ce_count > 0:
                successful_extractions += 1

            # Collect all named entities for grounding analysis
            named_entities = extraction.get("named_entities", [])
            all_entities.extend(named_entities)

            # Collect extracted objects for CompoundExpression analysis
            all_extracted_objects.append(extracted_obj)

        # Core success metrics
        result["success_metrics"]["compound_expressions"] = total_ce_count
        result["success_metrics"]["successful_extractions"] = successful_extractions
        result["success_metrics"]["primary_success"] = successful_extractions > 0

        # Aggregate CompoundExpression analysis across all extractions
        ce_analysis = {
            "total_compound_expressions": 0,
            "grounded_subjects": 0,
            "grounded_predicates": 0,
            "metpo_predicates": 0,
        }
        all_predicate_validations = []
        for extracted_obj in all_extracted_objects:
            obj_analysis = self._analyze_compound_expression_grounding(extracted_obj)
            ce_analysis["total_compound_expressions"] += obj_analysis["total_compound_expressions"]
            ce_analysis["grounded_subjects"] += obj_analysis["grounded_subjects"]
            ce_analysis["grounded_predicates"] += obj_analysis["grounded_predicates"]
            ce_analysis["metpo_predicates"] += obj_analysis["metpo_predicates"]
            all_predicate_validations.extend(obj_analysis.get("predicate_validation_details", []))

        # Calculate final rates
        total_ces = ce_analysis["total_compound_expressions"]
        ce_analysis["subject_grounding_rate"] = round(
            (ce_analysis["grounded_subjects"] / max(total_ces, 1)) * 100, 1
        )
        ce_analysis["predicate_grounding_rate"] = round(
            (ce_analysis["grounded_predicates"] / max(total_ces, 1)) * 100, 1
        )
        ce_analysis["metpo_predicate_usage"] = round(
            (ce_analysis["metpo_predicates"] / max(total_ces, 1)) * 100, 1
        )

        # Analyze predicate validation results
        predicate_analysis = self._analyze_predicate_validation(all_predicate_validations)
        ce_analysis["predicate_validation"] = predicate_analysis

        # Performance analysis using aggregated data
        result["performance"] = {
            "raw_output": self._analyze_raw_output(
                extractions[0].get("raw_completion_output", "") if extractions else ""
            ),
            "grounding": self._analyze_grounding(all_entities),
            "compound_expression_grounding": ce_analysis,
            "coverage": self._analyze_coverage(extractions[0] if extractions else {}),
            "span_distances": self._assess_span_distances(extractions),
            "verbatim_traceability": self._assess_verbatim_traceability(extractions),
            "strain_taxon_consistency": self._assess_strain_taxon_consistency(extractions),
        }

        # Generate insights
        self._generate_extraction_insights(result)

        return result

    def _empty_extraction_result(self, extraction_path: Path) -> dict[str, Any]:
        """Return empty result for failed extractions."""
        return {
            "extraction_path": str(extraction_path),
            "template_name": self._extract_template_name(extraction_path),
            "analysis_timestamp": datetime.now(UTC).isoformat(),
            "success_metrics": {"compound_expressions": 0, "primary_success": False},
            "performance": {
                "raw_output": {"populated_fields": 0, "total_entities": 0},
                "grounding": {"total": 0, "grounded": 0, "rate": 0},
                "coverage": {"span_rate": 0},
            },
            "issues": ["Failed to parse extraction file"],
            "strengths": [],
        }

    def _extract_template_name(self, extraction_path: Path) -> str:
        """Extract template name from extraction filename."""
        stem = extraction_path.stem
        parts = stem.split("_")
        if len(parts) >= 3:
            return "_".join(parts[:-2])  # Remove timestamp
        return parts[0]

    def _count_compound_expressions(self, extracted_object: dict) -> int:
        """Count valid CompoundExpressions."""
        count = 0
        for key, value in extracted_object.items():
            if key in self.universal_entities:
                continue

            if isinstance(value, list):
                for item in value:
                    if self._is_compound_expression(item):
                        count += 1
            elif self._is_compound_expression(value):
                count += 1

        return count

    def _is_compound_expression(self, item: Any) -> bool:
        """Check if item is valid CompoundExpression."""
        if not isinstance(item, dict):
            return False
        required = {"subject", "predicate", "object"}
        return all(key in item and item[key] for key in required)

    def _analyze_raw_output(self, raw_output: str) -> dict[str, Any]:
        """Analyze raw LLM completion quality."""
        if not raw_output:
            return {"populated_fields": 0, "total_entities": 0, "quality": "empty"}

        lines = raw_output.strip().split("\\n")
        populated_fields = 0
        total_entities = 0

        for line in lines:
            if ":" in line and not line.startswith(" "):
                field_value = ":".join(line.split(":")[1:]).strip()
                if field_value:
                    populated_fields += 1
                    entities = [e.strip() for e in field_value.split(";") if e.strip()]
                    total_entities += len(entities)

        quality = "excellent" if total_entities > 20 else "good" if total_entities > 10 else "poor"

        return {
            "populated_fields": populated_fields,
            "total_entities": total_entities,
            "avg_entities_per_field": total_entities / max(populated_fields, 1),
            "quality": quality,
        }

    def _analyze_grounding(self, named_entities: list[dict]) -> dict[str, Any]:
        """Analyze entity grounding quality with enhanced metrics."""
        total = len(named_entities)
        auto = sum(1 for e in named_entities if e.get("id", "").startswith("AUTO:"))
        grounded = total - auto

        # Ontology usage analysis
        ontologies = {}
        entity_duplicates = {}

        for entity in named_entities:
            entity_id = entity.get("id", "")
            entity.get("label", "")

            # Track ontology usage
            if ":" in entity_id and not entity_id.startswith("AUTO:"):
                ontology = entity_id.split(":")[0]
                ontologies[ontology] = ontologies.get(ontology, 0) + 1

            # Track entity duplication
            if entity_id:
                entity_duplicates[entity_id] = entity_duplicates.get(entity_id, 0) + 1

        # Find most duplicated entities (excluding expected NCBI taxonomy)
        duplicated_entities = {
            k: v for k, v in entity_duplicates.items() if v > 1 and not k.startswith("NCBITaxon:")
        }

        # Calculate auto vs grounded ratio
        auto_vs_grounded_ratio = auto / max(grounded, 1) if grounded > 0 else float("inf")

        return {
            "total": total,
            "grounded": grounded,
            "auto": auto,
            "rate": (grounded / max(total, 1)) * 100,
            "auto_vs_grounded_ratio": round(auto_vs_grounded_ratio, 2),
            "ontologies_used": ontologies,
            "ontology_diversity": len(ontologies),
            "duplicated_entities": duplicated_entities,
            "excessive_duplication": len(duplicated_entities) > 5,
        }

    def _analyze_compound_expression_grounding(self, extracted_obj: dict) -> dict[str, Any]:
        """Analyze grounding quality specifically for CompoundExpression objects."""
        total_ces = 0
        grounded_subjects = 0
        grounded_predicates = 0
        metpo_predicates = 0
        predicate_validation_details = []

        # Check all fields that might contain CompoundExpressions
        for field_name, field_value in extracted_obj.items():
            if isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, dict) and all(
                        k in item for k in ["subject", "predicate", "object"]
                    ):
                        total_ces += 1

                        # Check subject grounding
                        subject = item.get("subject", "")
                        if (
                            isinstance(subject, str)
                            and ":" in subject
                            and not subject.startswith("AUTO:")
                        ):
                            grounded_subjects += 1

                        # Check predicate grounding and validation
                        predicate = item.get("predicate", "")
                        if isinstance(predicate, str):
                            if ":" in predicate and not predicate.startswith("AUTO:"):
                                grounded_predicates += 1
                            if "METPO:" in str(predicate) or predicate in [
                                "uses_as_carbon_source",
                                "degrades",
                                "ferments",
                            ]:
                                metpo_predicates += 1

                            # Validate predicate against expected enumeration
                            validation_result = self._validate_predicate(field_name, predicate)
                            predicate_validation_details.append(
                                {
                                    "field": field_name,
                                    "predicate": predicate,
                                    "subject": subject,
                                    "object": item.get("object", ""),
                                    "expected_enum": validation_result["expected_enum"],
                                    "is_valid": validation_result["is_valid"],
                                    "reason": validation_result.get("reason", ""),
                                }
                            )

        return {
            "total_compound_expressions": total_ces,
            "grounded_subjects": grounded_subjects,
            "grounded_predicates": grounded_predicates,
            "metpo_predicates": metpo_predicates,
            "predicate_validation_details": predicate_validation_details,
            "subject_grounding_rate": round((grounded_subjects / max(total_ces, 1)) * 100, 1),
            "predicate_grounding_rate": round((grounded_predicates / max(total_ces, 1)) * 100, 1),
            "metpo_predicate_usage": round((metpo_predicates / max(total_ces, 1)) * 100, 1),
        }

    def _validate_predicate(self, field_name: str, predicate: str) -> dict[str, Any]:
        """Validate predicate against expected enumeration for the field."""
        # Load template enumerations if not already cached
        if not hasattr(self, "_template_enums"):
            self._template_enums = self._load_template_enumerations()

        # Determine expected enumeration based on field name and context
        expected_enum = self._get_expected_enumeration(field_name)

        if not expected_enum:
            return {
                "expected_enum": "unknown",
                "is_valid": True,  # Can't validate if we don't know the expected enum
                "reason": "No enumeration mapping found for this field",
            }

        # Check if predicate is in the expected enumeration
        enum_values = self._template_enums.get(expected_enum, {}).get("permissible_values", {})
        is_valid = predicate in enum_values

        return {
            "expected_enum": expected_enum,
            "is_valid": is_valid,
            "reason": "Valid METPO predicate" if is_valid else f"Not found in {expected_enum}",
            "available_values": list(enum_values.keys()) if not is_valid else None,
        }

    def _load_template_enumerations(self) -> dict[str, Any]:
        """Load enumeration definitions from template files."""
        enums = {}

        # Try to load from common template files
        template_paths = [
            "templates/chemical_utilization_populated.yaml",
            "templates/chemical_utilization_template_base.yaml",
            "templates/growth_conditions_populated.yaml",
            "templates/morphology_populated.yaml",
            "templates/taxa_populated.yaml",
            "templates/biochemical_populated.yaml",
        ]

        for template_path in template_paths:
            try:
                if Path(template_path).exists():
                    with Path(template_path).open() as f:
                        template_data = yaml.safe_load(f)
                        if "enums" in template_data:
                            enums.update(template_data["enums"])
            except Exception as e:
                print(f"Warning: Could not load template {template_path}: {e}")

        return enums

    def _get_expected_enumeration(self, field_name: str) -> str:
        """Map field names to their expected enumeration types."""
        # Field name to enumeration mapping
        field_enum_mapping = {
            "chemical_utilizations": "ChemicalInteractionPropertyEnum",
            "strain_relationships": "StrainRelationshipType",
            "growth_condition_relationships": "GrowthConditionType",
            "environment_relationships": "EnvironmentRelationshipType",
            "cell_shape_relationships": "MorphologyType",
            "cell_arrangement_relationships": "MorphologyType",
            "gram_staining_relationships": "MorphologyType",
            "motility_relationships": "MorphologyType",
            "spore_formation_relationships": "MorphologyType",
            "cell_wall_relationships": "MorphologyType",
            "cellular_inclusion_relationships": "MorphologyType",
            "enzyme_relationships": "BiochemicalInteractionType",
            "api_result_relationships": "BiochemicalInteractionType",
            "fatty_acid_relationships": "BiochemicalInteractionType",
        }

        return field_enum_mapping.get(field_name)

    def _analyze_predicate_validation(self, validation_details: list[dict]) -> dict[str, Any]:
        """Analyze predicate validation results across all compound expressions."""
        if not validation_details:
            return {
                "total_predicates": 0,
                "valid_predicates": 0,
                "compliance_rate": 0.0,
                "enumeration_usage": {},
                "invalid_predicates": [],
                "summary": "No predicate validation data available",
            }

        total_predicates = len(validation_details)
        valid_predicates = sum(1 for v in validation_details if v.get("is_valid", False))
        compliance_rate = round((valid_predicates / total_predicates) * 100, 1)

        # Analyze enumeration usage
        enumeration_usage = {}
        invalid_predicates = []

        for validation in validation_details:
            enum_name = validation.get("expected_enum", "unknown")
            if enum_name not in enumeration_usage:
                enumeration_usage[enum_name] = {"total": 0, "valid": 0, "invalid_predicates": []}

            enumeration_usage[enum_name]["total"] += 1

            if validation.get("is_valid", False):
                enumeration_usage[enum_name]["valid"] += 1
            else:
                predicate_info = {
                    "predicate": validation.get("predicate", ""),
                    "field": validation.get("field", ""),
                    "expected_enum": enum_name,
                    "reason": validation.get("reason", ""),
                    "subject": validation.get("subject", ""),
                    "object": validation.get("object", ""),
                }
                enumeration_usage[enum_name]["invalid_predicates"].append(predicate_info)
                invalid_predicates.append(predicate_info)

        # Calculate compliance rates per enumeration
        for enum_name, data in enumeration_usage.items():
            data["compliance_rate"] = round((data["valid"] / max(data["total"], 1)) * 100, 1)

        return {
            "total_predicates": total_predicates,
            "valid_predicates": valid_predicates,
            "compliance_rate": compliance_rate,
            "enumeration_usage": enumeration_usage,
            "invalid_predicates": invalid_predicates,
            "summary": f"{compliance_rate}% predicate compliance ({valid_predicates}/{total_predicates} valid)",
        }

    def _analyze_coverage(self, extraction: dict) -> dict[str, Any]:
        """Analyze text coverage."""
        named_entities = extraction.get("named_entities", [])
        entities_with_spans = sum(1 for e in named_entities if e.get("original_spans"))

        return {
            "entities_with_spans": entities_with_spans,
            "total_entities": len(named_entities),
            "span_rate": (entities_with_spans / max(len(named_entities), 1)) * 100,
        }

    def _assess_span_distances(self, extractions: list[dict]) -> dict[str, Any]:
        """Assess span distances in compound expressions for semantic coherence."""
        results = {
            "total_compound_expressions": 0,
            "expressions_with_spans": 0,
            "distance_distribution": {
                "close": 0,  # <100 chars
                "medium": 0,  # 100-500 chars
                "far": 0,  # >500 chars
                "cross_section": 0,  # spans in different parts
            },
            "detailed_analysis": [],
        }

        for extraction in extractions:
            if not isinstance(extraction, dict) or "extracted_object" not in extraction:
                continue

            extracted_obj = extraction["extracted_object"]
            named_entities = extraction.get("named_entities", [])

            # Build span lookup
            entity_spans = {}
            for entity in named_entities:
                entity_id = entity.get("id", "")
                spans = entity.get("original_spans", [])
                if spans:
                    entity_spans[entity_id] = spans

            # Analyze compound expressions
            for field_name, field_value in extracted_obj.items():
                if isinstance(field_value, list):
                    for item in field_value:
                        if isinstance(item, dict) and all(
                            k in item for k in ["subject", "predicate", "object"]
                        ):
                            results["total_compound_expressions"] += 1

                            subject_id = item.get("subject", "")
                            object_id = item.get("object", "")
                            predicate = item.get("predicate", "")

                            subject_spans = entity_spans.get(subject_id, [])
                            object_spans = entity_spans.get(object_id, [])

                            if subject_spans and object_spans:
                                results["expressions_with_spans"] += 1

                                # Calculate minimum distance between any subject/object spans
                                min_distance = float("inf")
                                closest_pair = None

                                for subj_span in subject_spans:
                                    for obj_span in object_spans:
                                        # Parse span format (handle both "243:247" strings and integers)
                                        if isinstance(subj_span, str) and ":" in subj_span:
                                            subj_start, subj_end = map(int, subj_span.split(":"))
                                        elif isinstance(subj_span, int):
                                            subj_start = subj_end = subj_span
                                        else:
                                            continue

                                        if isinstance(obj_span, str) and ":" in obj_span:
                                            obj_start, obj_end = map(int, obj_span.split(":"))
                                        elif isinstance(obj_span, int):
                                            obj_start = obj_end = obj_span
                                        else:
                                            continue

                                        # Calculate distance (gap between spans)
                                        if subj_end <= obj_start:
                                            distance = obj_start - subj_end
                                        elif obj_end <= subj_start:
                                            distance = subj_start - obj_end
                                        else:
                                            distance = 0  # Overlapping

                                        if distance < min_distance:
                                            min_distance = distance
                                            closest_pair = (subj_span, obj_span)

                                # Categorize distance
                                if min_distance < 100:
                                    category = "close"
                                elif min_distance < 500:
                                    category = "medium"
                                else:
                                    category = "far"

                                # Check for cross-section (title vs body)
                                def get_span_start(span):
                                    if isinstance(span, str) and ":" in span:
                                        return int(span.split(":")[0])
                                    if isinstance(span, int):
                                        return span
                                    return 0

                                is_cross_section = any(
                                    get_span_start(span) < 100 for span in subject_spans
                                ) and any(get_span_start(span) > 500 for span in object_spans)
                                if is_cross_section:
                                    category = "cross_section"

                                results["distance_distribution"][category] += 1

                                results["detailed_analysis"].append(
                                    {
                                        "field": field_name,
                                        "subject": subject_id,
                                        "predicate": predicate,
                                        "object": object_id,
                                        "min_distance": min_distance,
                                        "category": category,
                                        "subject_spans": subject_spans,
                                        "object_spans": object_spans,
                                        "closest_pair": closest_pair,
                                    }
                                )

        # Calculate percentages
        total_with_spans = results["expressions_with_spans"]
        if total_with_spans > 0:
            categories = list(results["distance_distribution"].keys())
            for category in categories:
                count = results["distance_distribution"][category]
                results["distance_distribution"][f"{category}_percentage"] = round(
                    count / total_with_spans * 100, 1
                )

        return results

    def _assess_verbatim_traceability(self, extractions: list[dict]) -> dict[str, Any]:
        """Assess verbatim traceability through extraction pipeline."""
        results = {
            "documents_analyzed": 0,
            "traceability_issues": [],
            "entity_traceability": [],
            "content_extraction_success": 0,
        }

        for doc_idx, extraction in enumerate(extractions):
            if not isinstance(extraction, dict):
                continue

            results["documents_analyzed"] += 1

            # Extract input content (handle JSON format)
            input_text = extraction.get("input_text", "")
            content_text = self._extract_content_text(input_text)

            if not content_text:
                results["traceability_issues"].append(
                    {
                        "doc_index": doc_idx,
                        "issue": "Could not extract content from input_text",
                        "input_text_type": type(input_text).__name__,
                    }
                )
                continue

            results["content_extraction_success"] += 1

            # Check entity span verification with enhanced diagnostics
            named_entities = extraction.get("named_entities", [])

            for entity in named_entities:
                entity_id = entity.get("id", "")
                entity_label = entity.get("label", "")
                spans = entity.get("original_spans", [])

                # Verify entity appears in content at specified spans
                span_matches = self._verify_spans(content_text, entity_label, spans)

                results["entity_traceability"].append(
                    {
                        "doc_index": doc_idx,
                        "entity_id": entity_id,
                        "entity_label": entity_label,
                        "spans_verified": span_matches["all_match"],
                        "spans_total": len(spans),
                        "spans_matched": span_matches["matched_count"],
                        "prefix_matches": span_matches["prefix_matches"],
                        "off_by_one_errors": span_matches["off_by_one_errors"],
                        "span_coverage_rate": span_matches["span_coverage_rate"],
                        "prefix_match_rate": span_matches["prefix_match_rate"],
                    }
                )

        # Aggregate span quality metrics
        all_entities = results["entity_traceability"]
        if all_entities:
            total_entities = len(all_entities)
            entities_with_spans = sum(1 for e in all_entities if e["spans_total"] > 0)
            exact_match_entities = sum(1 for e in all_entities if e["spans_verified"])
            prefix_match_entities = sum(1 for e in all_entities if e["prefix_matches"] > 0)
            off_by_one_entities = sum(1 for e in all_entities if e["off_by_one_errors"] > 0)

            results["span_quality_summary"] = {
                "entities_with_spans": entities_with_spans,
                "span_coverage_rate": round(entities_with_spans / max(total_entities, 1) * 100, 1),
                "exact_match_rate": round(exact_match_entities / max(total_entities, 1) * 100, 1),
                "prefix_match_rate": round(prefix_match_entities / max(total_entities, 1) * 100, 1),
                "off_by_one_rate": round(off_by_one_entities / max(total_entities, 1) * 100, 1),
                "span_diagnostic": "Systematic off-by-one truncation"
                if off_by_one_entities > total_entities * 0.8
                else "Mixed patterns",
            }

        return results

    def _assess_strain_taxon_consistency(self, extractions: list[dict]) -> dict[str, Any]:
        """Assess consistency between strain subjects and taxon relationships."""
        results = {
            "documents_analyzed": 0,
            "consistency_checks": [],
            "violations": [],
            "strain_usage_patterns": defaultdict(list),
        }

        for doc_idx, extraction in enumerate(extractions):
            if not isinstance(extraction, dict) or "extracted_object" not in extraction:
                continue

            results["documents_analyzed"] += 1
            extracted_obj = extraction["extracted_object"]

            # Extract strain subjects from all compound expressions
            strain_subjects = set()
            for field_name, field_value in extracted_obj.items():
                if isinstance(field_value, list):
                    for item in field_value:
                        if isinstance(item, dict) and "subject" in item:
                            subject = item.get("subject", "")
                            if subject.startswith("AUTO:"):
                                # Extract strain identifier (clean up encoding)
                                strain_id = (
                                    subject.replace("AUTO:", "")
                                    .replace("%20", " ")
                                    .replace("%2034211", " 34211")
                                )
                                strain_subjects.add(strain_id)
                                results["strain_usage_patterns"][strain_id].append(
                                    f"{field_name}_{doc_idx}"
                                )

            # Extract strain subjects from strain relationships
            strain_rels = extracted_obj.get("strain_relationships", [])
            strain_rel_subjects = set()
            strain_to_taxon = {}

            for rel in strain_rels:
                if isinstance(rel, dict):
                    subject = rel.get("subject", "")
                    object_taxon = rel.get("object", "")

                    if subject.startswith("AUTO:"):
                        strain_id = subject.replace("AUTO:", "").replace("%20", " ")
                        strain_rel_subjects.add(strain_id)
                        strain_to_taxon[strain_id] = object_taxon
                        results["strain_usage_patterns"][strain_id].append(
                            f"strain_relationship_{doc_idx}"
                        )

            # Check consistency
            check_result = {
                "doc_index": doc_idx,
                "compound_expression_strains": list(strain_subjects),
                "relationship_strains": list(strain_rel_subjects),
                "consistent_strains": list(strain_subjects & strain_rel_subjects),
                "orphan_ce_strains": list(strain_subjects - strain_rel_subjects),
                "orphan_rel_strains": list(strain_rel_subjects - strain_subjects),
                "strain_taxon_mappings": strain_to_taxon,
            }

            results["consistency_checks"].append(check_result)

            # Flag violations
            if check_result["orphan_ce_strains"]:
                results["violations"].append(
                    {
                        "doc_index": doc_idx,
                        "type": "compound_expression_strain_without_relationship",
                        "strains": check_result["orphan_ce_strains"],
                    }
                )

            if check_result["orphan_rel_strains"]:
                results["violations"].append(
                    {
                        "doc_index": doc_idx,
                        "type": "relationship_strain_without_usage",
                        "strains": check_result["orphan_rel_strains"],
                    }
                )

        return results

    def _extract_content_text(self, input_text: Any) -> str:
        """Extract content from input_text (handles JSON, YAML, or raw text)."""
        if isinstance(input_text, str):
            # Try to parse as JSON first
            try:
                data = json.loads(input_text)
                return data.get("content", input_text)
            except json.JSONDecodeError:
                # Try YAML parsing as fallback
                try:
                    data = yaml.safe_load(input_text)
                    if isinstance(data, dict) and "content" in data:
                        return data["content"]
                except yaml.YAMLError:
                    pass
                return input_text
        elif isinstance(input_text, dict):
            return input_text.get("content", str(input_text))
        else:
            return str(input_text)

    def _verify_spans(self, content: str, entity_label: str, spans: list) -> dict[str, Any]:
        """Verify entity appears at specified span coordinates with diagnostic details."""
        exact_matches = 0
        prefix_matches = 0
        valid_spans = 0
        off_by_one = 0
        off_by_two = 0

        for span in spans:
            try:
                # Handle both string "start:end" and integer formats
                if isinstance(span, str) and ":" in span:
                    start, end = map(int, span.split(":"))
                elif isinstance(span, int):
                    start = end = span
                else:
                    continue

                if start < len(content) and end <= len(content):
                    valid_spans += 1
                    span_text = content[start:end]

                    if span_text == entity_label:
                        exact_matches += 1
                    elif entity_label.startswith(span_text) and span_text:
                        prefix_matches += 1
                        char_diff = len(entity_label) - len(span_text)
                        if char_diff == 1:
                            off_by_one += 1
                        elif char_diff == 2:
                            off_by_two += 1

            except (ValueError, TypeError):
                continue

        return {
            "all_match": exact_matches == len(spans) and len(spans) > 0,
            "matched_count": exact_matches,
            "total_spans": len(spans),
            "valid_spans": valid_spans,
            "prefix_matches": prefix_matches,
            "off_by_one_errors": off_by_one,
            "off_by_two_errors": off_by_two,
            "span_coverage_rate": round(valid_spans / max(len(spans), 1) * 100, 1),
            "prefix_match_rate": round(prefix_matches / max(valid_spans, 1) * 100, 1),
        }

    def _generate_extraction_insights(self, result: dict):
        """Generate insights for extraction performance."""
        performance = result["performance"]
        success = result["success_metrics"]

        # Primary success assessment
        if success["compound_expressions"] == 0:
            result["issues"].append("CRITICAL: No CompoundExpressions extracted")
        elif success["compound_expressions"] > 10:
            result["strengths"].append(
                f"Excellent relationship extraction: {success['compound_expressions']} CEs"
            )

        # Raw output quality
        raw_quality = performance["raw_output"]["quality"]
        if raw_quality == "poor":
            result["issues"].append("Poor raw LLM output quality")
        elif raw_quality == "excellent":
            result["strengths"].append("Excellent raw LLM output richness")

        # Grounding quality
        grounding_rate = performance["grounding"]["rate"]
        if grounding_rate < 60:
            result["issues"].append(f"Low grounding rate: {grounding_rate:.1f}%")
        elif grounding_rate > 80:
            result["strengths"].append(f"Excellent grounding rate: {grounding_rate:.1f}%")

        # Predicate validation insights
        predicate_validation = performance.get("compound_expression_grounding", {}).get(
            "predicate_validation", {}
        )
        if predicate_validation:
            compliance_rate = predicate_validation.get("compliance_rate", 0)
            if compliance_rate < 80:
                result["issues"].append(f"Low predicate compliance: {compliance_rate:.1f}%")
                invalid_count = len(predicate_validation.get("invalid_predicates", []))
                if invalid_count > 0:
                    result["issues"].append(f"Found {invalid_count} invalid predicates")
            elif compliance_rate > 95:
                result["strengths"].append(
                    f"Excellent predicate compliance: {compliance_rate:.1f}%"
                )

        # Span distance insights
        span_distances = performance.get("span_distances", {})
        if span_distances.get("expressions_with_spans", 0) > 0:
            dist = span_distances.get("distance_distribution", {})
            far_percentage = dist.get("far_percentage", 0)
            close_percentage = dist.get("close_percentage", 0)

            if far_percentage > 20:
                result["issues"].append(
                    f"Many far-apart relationships: {far_percentage:.1f}% (may indicate weak semantic links)"
                )
            elif close_percentage > 40:
                result["strengths"].append(
                    f"Good semantic proximity: {close_percentage:.1f}% close relationships"
                )

        # Verbatim traceability insights
        traceability = performance.get("verbatim_traceability", {})
        if traceability.get("documents_analyzed", 0) > 0:
            entities = traceability.get("entity_traceability", [])
            if entities:
                verified_entities = sum(1 for e in entities if e.get("spans_verified", False))
                verification_rate = (verified_entities / len(entities)) * 100

                if verification_rate < 20:
                    result["issues"].append(
                        f"Low span verification: {verification_rate:.1f}% (potential preprocessing issues)"
                    )
                elif verification_rate > 70:
                    result["strengths"].append(f"Excellent span accuracy: {verification_rate:.1f}%")

        # Strain-taxon consistency insights
        consistency = performance.get("strain_taxon_consistency", {})
        violations = consistency.get("violations", [])
        if violations:
            violation_count = len(violations)
            docs_analyzed = consistency.get("documents_analyzed", 1)
            violation_rate = violation_count / docs_analyzed

            if violation_rate > 1:
                result["issues"].append(
                    f"Strain-taxon inconsistencies: {violation_count} violations across {docs_analyzed} documents"
                )

            # Categorize violation types
            violation_types = {}
            for v in violations:
                vtype = v.get("type", "unknown")
                violation_types[vtype] = violation_types.get(vtype, 0) + 1

            for vtype, count in violation_types.items():
                if count > 2:
                    result["issues"].append(f"Repeated {vtype}: {count} cases")
        else:
            docs_with_strains = sum(
                1
                for check in consistency.get("consistency_checks", [])
                if check.get("compound_expression_strains") or check.get("relationship_strains")
            )
            if docs_with_strains > 0:
                result["strengths"].append("Perfect strain-taxon consistency across all documents")

    # ===== UTILITY METHODS =====

    def _find_tree_root(self, classes: dict) -> dict | None:
        """Find tree root class."""
        for _class_name, class_def in classes.items():
            if class_def.get("tree_root"):
                return class_def
        return None

    def cross_template_analysis(self, template_results: list[dict]) -> dict[str, Any]:
        """Analyze patterns across multiple templates for optimization."""
        if len(template_results) < 2:
            return {"message": "Need multiple templates for cross-analysis"}

        # Collect patterns
        all_patterns = defaultdict(list)
        for result in template_results:
            template_name = result["template_name"]
            patterns = result.get("patterns", {})

            # Collect entity types and annotators
            for entity in patterns.get("entity_types", []):
                all_patterns["entities"].append(
                    {
                        "template": template_name,
                        "name": entity["name"],
                        "annotators": entity["annotators"],
                    }
                )

        # Find best practices to propagate
        best_practices = []
        annotator_patterns = defaultdict(set)

        for entity_info in all_patterns["entities"]:
            annotators = entity_info["annotators"]
            if annotators and len(annotators.split(",")) >= 2:
                annotator_patterns[entity_info["name"]].add(annotators)

        return {
            "cross_template_patterns": dict(all_patterns),
            "best_practices": best_practices,
            "recommendations": [
                "Standardize annotator patterns across similar entity types",
                "Propagate successful CompoundExpression patterns",
                "Harmonize field description patterns",
            ],
        }


# ===== CLI INTERFACE =====


@click.group()
def cli():
    """METPO Literature Mining Assessment Tool"""


@cli.command()
@click.argument("templates_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file")
@click.option("--pattern", default="*_base.yaml", help="Template file pattern")
def analyze_templates(templates_dir, output, pattern):
    """Phase 1: Analyze template design quality in isolation."""
    assessor = MetpoAssessor()
    template_files = list(templates_dir.glob(pattern))

    if not template_files:
        click.echo(f"No templates found with pattern {pattern}")
        return

    click.echo(f"Analyzing {len(template_files)} templates...")

    results = []
    for template_file in template_files:
        click.echo(f"  {template_file.name}")
        result = assessor.analyze_template(template_file)
        results.append(result)

    # Cross-template analysis
    cross_analysis = assessor.cross_template_analysis(results)

    # Generate report
    report = generate_template_report(results, cross_analysis)

    if output:
        output.write_text(report)
        click.echo(f"Template analysis written to {output}")
    else:
        click.echo("\\n" + report)


@cli.command()
@click.argument("extractions_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file")
@click.option("--pattern", default="*.yaml", help="Extraction file pattern")
def analyze_extractions(extractions_dir, output, pattern):
    """Phase 2: Analyze extraction output performance."""
    assessor = MetpoAssessor()
    extraction_files = list(extractions_dir.glob(pattern))

    if not extraction_files:
        click.echo(f"No extractions found with pattern {pattern}")
        return

    click.echo(f"Analyzing {len(extraction_files)} extractions...")

    results = []
    for extraction_file in extraction_files:
        click.echo(f"  {extraction_file.name}")
        result = assessor.analyze_extraction(extraction_file)
        results.append(result)

    # Generate report
    report = generate_extraction_report(results)

    if output:
        output.write_text(report)
        click.echo(f"Extraction analysis written to {output}")
    else:
        click.echo("\\n" + report)


def generate_template_report(results: list[dict], cross_analysis: dict) -> str:
    """Generate template analysis report in YAML format."""
    report = {
        "generated": datetime.now(UTC).strftime("%Y-%m-%d %H:%M"),
        "summary": {"templates_analyzed": len(results)},
        "templates": {},
    }

    # Individual template results
    for result in results:
        name = result["template_name"]
        compliance = result["compliance"]

        report["templates"][name] = {
            "compliance_metrics": {
                "compound_expression_compliance": round(
                    compliance["compound_expressions"]["compliance_rate"], 1
                ),
                "semicolon_requests": round(compliance["semicolon_requests"]["rate"], 1),
                "multivalued_fields": round(compliance["multivalued_fields"]["rate"], 1),
                "well_annotated_entities": round(compliance["annotator_quality"]["rate"], 1),
            },
            "issues": result["issues"],
            "recommendations": result["recommendations"],
        }

    return yaml.dump(report, default_flow_style=False, sort_keys=False)


def generate_extraction_report(results: list[dict]) -> str:
    """Generate extraction performance report in YAML format."""
    total = len(results)
    successful = sum(1 for r in results if r["success_metrics"]["primary_success"])
    total_ces = sum(r["success_metrics"]["compound_expressions"] for r in results)

    report = {
        "generated": datetime.now(UTC).strftime("%Y-%m-%d %H:%M"),
        "summary": {
            "extractions_analyzed": total,
            "successful_extractions": successful,
            "success_rate": round(successful / max(total, 1) * 100, 1),
            "total_compound_expressions": total_ces,
            "average_ces_per_extraction": round(total_ces / max(total, 1), 1),
        },
        "templates": {},
    }

    # Group by template
    by_template = defaultdict(list)
    for result in results:
        template_name = result["template_name"]
        by_template[template_name].append(result)

    for template_name, template_results in by_template.items():
        successful_count = sum(
            1 for r in template_results if r["success_metrics"]["primary_success"]
        )
        total_count = len(template_results)
        ces = sum(r["success_metrics"]["compound_expressions"] for r in template_results)
        abstracts_processed = sum(r.get("abstracts_processed", 1) for r in template_results)

        # Aggregate grounding metrics
        avg_grounding = sum(r["performance"]["grounding"]["rate"] for r in template_results) / len(
            template_results
        )
        avg_auto_vs_grounded = sum(
            r["performance"]["grounding"]["auto_vs_grounded_ratio"] for r in template_results
        ) / len(template_results)

        # Aggregate CompoundExpression metrics
        avg_subject_grounding = sum(
            r["performance"]["compound_expression_grounding"]["subject_grounding_rate"]
            for r in template_results
        ) / len(template_results)
        avg_predicate_grounding = sum(
            r["performance"]["compound_expression_grounding"]["predicate_grounding_rate"]
            for r in template_results
        ) / len(template_results)
        avg_metpo_usage = sum(
            r["performance"]["compound_expression_grounding"]["metpo_predicate_usage"]
            for r in template_results
        ) / len(template_results)

        # Aggregate ontology usage
        all_ontologies = {}
        all_duplicates = {}
        for r in template_results:
            grounding = r["performance"]["grounding"]
            for ont, count in grounding.get("ontologies_used", {}).items():
                all_ontologies[ont] = all_ontologies.get(ont, 0) + count
            for ent, count in grounding.get("duplicated_entities", {}).items():
                all_duplicates[ent] = all_duplicates.get(ent, 0) + count

        # Aggregate advanced metrics
        advanced_metrics = {}
        if template_results and "performance" in template_results[0]:
            perf = template_results[0]["performance"]

            # Span distances (from latest result)
            if "span_distances" in perf:
                span_data = perf["span_distances"]
                advanced_metrics["span_distances"] = {
                    "total_compound_expressions": span_data.get("total_compound_expressions", 0),
                    "expressions_with_spans": span_data.get("expressions_with_spans", 0),
                    "distance_distribution": span_data.get("distance_distribution", {}),
                }

            # Verbatim traceability (from latest result) with enhanced diagnostics
            if "verbatim_traceability" in perf:
                trace_data = perf["verbatim_traceability"]
                span_summary = trace_data.get("span_quality_summary", {})
                advanced_metrics["verbatim_traceability"] = {
                    "documents_analyzed": trace_data.get("documents_analyzed", 0),
                    "content_extraction_success": trace_data.get("content_extraction_success", 0),
                    "span_coverage_rate": span_summary.get("span_coverage_rate", 0),
                    "exact_match_rate": span_summary.get("exact_match_rate", 0),
                    "prefix_match_rate": span_summary.get("prefix_match_rate", 0),
                    "off_by_one_rate": span_summary.get("off_by_one_rate", 0),
                    "span_diagnostic": span_summary.get(
                        "span_diagnostic", "No diagnostic available"
                    ),
                }

            # Strain-taxon consistency (from latest result)
            if "strain_taxon_consistency" in perf:
                consistency_data = perf["strain_taxon_consistency"]
                violations = consistency_data.get("violations", [])
                advanced_metrics["strain_taxon_consistency"] = {
                    "documents_analyzed": consistency_data.get("documents_analyzed", 0),
                    "total_violations": len(violations),
                    "violation_types": {},
                }
                # Count violation types
                for violation in violations:
                    vtype = violation.get("type", "unknown")
                    advanced_metrics["strain_taxon_consistency"]["violation_types"][vtype] = (
                        advanced_metrics["strain_taxon_consistency"]["violation_types"].get(
                            vtype, 0
                        )
                        + 1
                    )

        template_report = {
            "abstracts_processed": abstracts_processed,
            "success_rate": f"{successful_count}/{total_count}",
            "success_percentage": round(successful_count / total_count * 100, 1),
            "compound_expressions": ces,
            "average_ces": round(ces / total_count, 1),
            "grounding_metrics": {
                "overall_grounding_rate": round(avg_grounding, 1),
                "auto_vs_grounded_ratio": round(avg_auto_vs_grounded, 2),
                "subject_grounding_rate": round(avg_subject_grounding, 1),
                "predicate_grounding_rate": round(avg_predicate_grounding, 1),
                "metpo_predicate_usage": round(avg_metpo_usage, 1),
            },
            "ontology_usage": all_ontologies,
            "problematic_duplicates": {k: v for k, v in all_duplicates.items() if v > 2},
        }

        # Add advanced metrics if available
        if advanced_metrics:
            template_report["advanced_metrics"] = advanced_metrics

        report["templates"][template_name] = template_report

    return yaml.dump(report, default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    cli()
