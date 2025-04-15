from cowrangler.learners.drop_learner import DropColumnLearner
from cowrangler.learners.missing_values_learner import ImputeMissingLearner
from cowrangler.learners.encoding_learner import EncodeCategoricalLearner
from cowrangler.learners.split_learner import SplitColumnLearner
from cowrangler.learners.typecast_learner import TypecastColumnLearner
from cowrangler.data_analysis import DataAnalyzer
from cowrangler.ranking_system import RankingSystem


class SuggestionEngine:
    def __init__(self, data_analyzer):
        self.data_analyzer = data_analyzer
        self.learners = []
        self.ranking_system = RankingSystem()
        self._initialize_learners()
    
    def _initialize_learners(self):
        """Initialize all learners"""
        # Add the drop column learner
        self.learners.append(DropColumnLearner(self.data_analyzer))
        self.learners.append(ImputeMissingLearner(self.data_analyzer))
        self.learners.append(EncodeCategoricalLearner(self.data_analyzer))
        self.learners.append(SplitColumnLearner(self.data_analyzer))
        self.learners.append(TypecastColumnLearner(self.data_analyzer))
        # Add other learners as they are implemented
        # self.learners.append(SplitLearner(self.data_analyzer))
        # etc.
    
    def generate_suggestions(self, max_suggestions=10):
        """Generate and rank suggestions from all learners"""
        all_suggestions = []
        
        # Collect suggestions from all learners
        for learner in self.learners:
            learner_suggestions = learner.generate_suggestions()
            all_suggestions.extend(learner_suggestions)
        
        # Rank suggestions by quality improvement score
        # ranked_suggestions = sorted(
        #     all_suggestions,
        #     key=lambda x: x.get("quality_improvement", 0),
        #     reverse=True
        # )
        ranked_suggestions = self.ranking_system.rank_suggestions(
            self.data_analyzer, 
            all_suggestions
        )
        
        # Return top N suggestions
        return ranked_suggestions[:max_suggestions]
    
    def apply_transformation(self, suggestion):
        """Apply a transformation based on the suggestion type"""
        # Find appropriate learner for this suggestion type
        for learner in self.learners:
            if isinstance(learner, DropColumnLearner) and suggestion["type"] == "drop_column":
                return learner.apply_transformation(suggestion)
            elif isinstance(learner, ImputeMissingLearner) and suggestion["type"] == "impute_missing":
                return learner.apply_transformation(suggestion)
            elif isinstance(learner, EncodeCategoricalLearner) and suggestion["type"] == "encode_categorical":
                return learner.apply_transformation(suggestion)
            elif isinstance(learner, SplitColumnLearner) and suggestion["type"] == "split_column":
                return learner.apply_transformation(suggestion)
            elif isinstance(learner, TypecastColumnLearner) and suggestion["type"] == "typecast_column":
                return learner.apply_transformation(suggestion)

        return False