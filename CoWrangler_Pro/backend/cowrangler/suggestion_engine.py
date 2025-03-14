from cowrangler.learners.drop_learner import DropColumnLearner

class SuggestionEngine:
    def __init__(self, data_analyzer):
        self.data_analyzer = data_analyzer
        self.learners = []
        self._initialize_learners()
    
    def _initialize_learners(self):
        """Initialize all learners"""
        # Add the drop column learner
        self.learners.append(DropColumnLearner(self.data_analyzer))
        
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
        ranked_suggestions = sorted(
            all_suggestions,
            key=lambda x: x.get("quality_improvement", 0),
            reverse=True
        )
        
        # Return top N suggestions
        return ranked_suggestions[:max_suggestions]
    
    def apply_transformation(self, suggestion):
        """Apply a transformation based on the suggestion type"""
        # Find appropriate learner for this suggestion type
        for learner in self.learners:
            if isinstance(learner, DropColumnLearner) and suggestion["type"] == "drop_column":
                return learner.apply_transformation(suggestion)
        
        return False